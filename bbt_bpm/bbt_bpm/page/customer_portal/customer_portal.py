from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from datetime import timedelta,date
import datetime
import calendar
import json
import time
from frappe import _
import requests
import json
from frappe.utils import cint, flt, get_datetime, datetime, date_diff, today, nowdate, getdate
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime

@frappe.whitelist()
def get_items_data(filters):
	filters = json.loads(filters)
	items_data = frappe.db.sql("""SELECT name, item_group, description, no_of_items_can_be_packed, carton, book_language from `tabItem` where {0} """.format(get_filters_codition(filters)), as_dict=1)
		
	for row in items_data:
		item_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("name")), as_dict=1)
		carton_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("carton")), as_dict=1)
		item_rate = frappe.db.get_value("Item Price", {"item_code":row.get("name")}, "price_list_rate")
		row["rate"] = item_rate
		row["stock_in_qty"] = item_qty[0].get("actual_qty") if item_qty[0] else 0
		row["carton_qty"] = carton_qty[0].get("actual_qty") if carton_qty[0] else 0

	path = 'bbt_bpm/bbt_bpm/page/customer_portal/customer_portal.html'
	html=frappe.render_template(path,{'data':items_data})
	return {'html':html}


def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("language"):
		conditions += " and book_language = '{0}'".format(filters.get('language'))
	return conditions


@frappe.whitelist()
def add_to_cart_item(filters):
	data = json.loads(filters)
	order_qty = 0.0
	if not data.get("order_qty"):
		order_qty = flt(data.get("cartan_order_qty"))*flt(data.get("no_of_items_can_be_packed"))
	else:
		order_qty = data.get("order_qty")

	item = frappe.db.get_values("Item", {"name":data.get("item")}, ["item_name", "description", "item_group"])
	if not frappe.db.get_value("Add To Cart", {"name":frappe.session.user}, "name"):
		doc=frappe.new_doc("Add To Cart")
		doc.user = frappe.session.user
		doc.append("items", {
			"item_code": data.get("item"),
			"item_name": item[0][0],
			"description": item[0][1],
			"item_group": item[0][2],
			"rate": data.get("rate"),
			"stock_in_nos": data.get("stock_in_qty"),
			"stock_in_cartons": data.get("carton_qty"),
			"book_per_carton": data.get("no_of_items_can_be_packed"),
			"ordered_qty_in_nos": order_qty,
			"ordered_qty_in_cartons": flt(data.get("cartan_order_qty")),
			"language": data.get("langname"),
			"amount": flt(data.get("rate"))*flt(order_qty)
		})
		doc.save(ignore_permissions=True)
	else:
		doc=frappe.get_doc("Add To Cart", frappe.session.user)
		doc.append("items", {
			"item_code": data.get("item"),
			"item_name": item[0][0],
			"description": item[0][1],
			"item_group": item[0][2],
			"rate": data.get("rate"),
			"stock_in_nos": data.get("stock_in_qty"),
			"stock_in_cartons": data.get("carton_qty"),
			"book_per_carton": data.get("no_of_items_can_be_packed"),
			"ordered_qty_in_nos": order_qty,
			"ordered_qty_in_cartons": flt(data.get("cartan_order_qty")),
			"language": data.get("language"),
			"amount": flt(data.get("rate"))*flt(order_qty)
		})
		doc.save(ignore_permissions=True)


@frappe.whitelist()
def add_to_cart_details(user):
	add_to_cart = frappe.db.sql("""SELECT name, item_code, item_group, description, rate, language, stock_in_nos, stock_in_cartons, book_per_carton, ordered_qty_in_nos, ordered_qty_in_cartons, amount from `tabAdd To Cart Item` where parent='{0}' """.format(user), as_dict=1)

	add_qty =  frappe.db.sql("""SELECT sum(ordered_qty_in_nos) as total_ordered_qty, sum(ordered_qty_in_cartons) as total_cartons_qty, sum(amount) as total_amount from `tabAdd To Cart Item` where parent='{0}' """.format(user), as_dict=1)
	for row in add_to_cart:
		row["total_ordered_qty"] = add_qty[0].get("total_ordered_qty")
		row["total_cartons_qty"] = add_qty[0].get("total_cartons_qty")
		row["total_amount"] = add_qty[0].get("total_amount")

	path = 'bbt_bpm/bbt_bpm/page/customer_portal/add_to_cart.html'
	html=frappe.render_template(path,{'data':add_to_cart})
	return {'html':html}


@frappe.whitelist()
def new_order(client_feedback):
	user = frappe.session.user
	data = frappe.db.sql("""SELECT item_code, item_name, item_group, description, rate, language, stock_in_nos, stock_in_cartons, book_per_carton, ordered_qty_in_nos, ordered_qty_in_cartons from `tabAdd To Cart Item` where parent='{0}' """.format(user), as_dict=1)
	customer = frappe.db.get_values("Customer", {"user":frappe.session.user}, ["name", "company", "default_currency", "default_price_list"])

	if frappe.db.get_value("Add To Cart", {"name":frappe.session.user}, "name") and customer:
		doc=frappe.new_doc("Sales Order")
		doc.customer = customer[0][0] if customer[0][0] else ""
		doc.company = customer[0][1] if customer[0][1] else ""
		doc.delivery_date = today()
		doc.currency = customer[0][2] if customer[0][2] else ""
		doc.selling_price_list = customer[0][3] if customer[0][3] else ""  
		for row in data:
			item_taxes_template = ""
			if customer[0][2] == "USD" and row.get("item_group")=="Poster" or row.get("item_group")=="CD":
				hsn_code = frappe.db.get_value("Item", {"name": row.get("item_code")}, "gst_hsn_code")
				item_taxes_template += frappe.db.get_value("Item Tax", {"parent":hsn_code, "item_tax_template":["like", "IGST%"]}, "item_tax_template")
			elif customer[0][1] == "Sri Sri Sitaram Seva Trust" and row.get("item_group")=="Poster" or row.get("item_group")=="CD":
				item_taxes_template += frappe.db.get_value("Item Tax", {"parent":hsn_code, "item_tax_template":["like", "CGST+SGST%"]}, "item_tax_template")
			doc.append("items", {
				"item_code": row.get("item_code"),
				"item_name": row.get("item_name"),
				"item_group": row.get("item_group"),
				"description":row.get("description"),
				"rate": flt(row.get("rate")),
				"qty":flt(row.get("ordered_qty_in_nos")),
				"uom":frappe.db.get_value("Item", {"name":row.get("item_code")}, "stock_uom"),
				"item_tax_template": item_taxes_template
				# "warehouse": "Stores - SRST"
			})
		doc.save()
		doc.add_comment('Comment', text=client_feedback)
		frappe.delete_doc('Add To Cart', frappe.session.user)
		frappe.db.commit()
	return True

@frappe.whitelist()
def delete_add_to_cart_item(user, name):
	data = json.loads(name)
	for row in data:
		frappe.delete_doc('Add To Cart Item', row)
		frappe.db.commit()
	return True


@frappe.whitelist()
def update_qty_on_cart(item, language, order_qty, rate):
	amount = 0.0
	amount = flt(order_qty)*flt(rate)
	frappe.db.set_value("Add To Cart Item", {"item_code":item, "language":language}, {"ordered_qty_in_nos":order_qty, "amount":amount})
	frappe.db.commit()


@frappe.whitelist()
def update_cartons_qty_on_cart(item, language, cartan_order_qty, rate, book_per_cartons):
	amount = 0.0
	order_qty = flt(book_per_cartons)*flt(cartan_order_qty)
	amount = flt(order_qty)*flt(rate)
	frappe.db.set_value("Add To Cart Item", {"item_code":item, "language":language}, {"ordered_qty_in_cartons":cartan_order_qty, "amount":amount, "ordered_qty_in_nos":order_qty})
	frappe.db.commit()
	print("=============aaaaa", amount, order_qty)