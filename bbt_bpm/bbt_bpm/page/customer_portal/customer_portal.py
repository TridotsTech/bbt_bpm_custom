from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from datetime import timedelta,date
from frappe.utils import now
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
import math

@frappe.whitelist()
def get_items_data(filters):
	filters = json.loads(filters)
	#print(f'\n\n{filters}\n\n')
	items_data = frappe.db.sql("""SELECT name, item_group, description, no_of_items_can_be_packed, carton, book_language,publisher from `tabItem` where {0} ORDER BY description""".format(get_filters_codition(filters)), as_dict=1)
	#print(f'\n\n{items_data}\n\n')	
	for row in items_data:
		item_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("name")), as_dict=1)
		carton_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("carton")), as_dict=1)

		item_reserved_qty = frappe.db.sql("""SELECT item_code, sum(qty) as qty From `tabStock Blocking Unblocking Table` where item_code='{0}' """.format(row.get("name")), as_dict=1)
		cartons_reserved_qty = frappe.db.sql("""SELECT sum(qty) as qty From `tabStock Blocking Unblocking Table` where item_code='{0}' """.format(row.get("carton")), as_dict=1)
		
		stock_qty=0.0
		if item_qty[0] and item_reserved_qty[0]:
			stock_qty = abs(flt(item_qty[0].get("actual_qty"))-flt(item_reserved_qty[0].get("qty")))
		else:
			stock_qty=item_qty[0].get("actual_qty") if item_qty[0] else 0
		cartons_qty = 0.0
		if carton_qty[0] and cartons_reserved_qty[0]:
			cartons_qty = abs(flt(carton_qty[0].get("actual_qty"))-flt(cartons_reserved_qty[0].get("qty")))
		else:
			cartons_qty=carton_qty[0].get("actual_qty") if carton_qty[0] else 0

		allow_carton_qty = 0.0
		if row.get("no_of_items_can_be_packed"):
			allow_carton_qty = flt(stock_qty)/flt(row.get("no_of_items_can_be_packed"))
		
		customer_user = frappe.session.user
		customer_price_list = frappe.db.get_value("Customer", {"user":customer_user}, "default_price_list")
		item_rate = frappe.db.get_value("Item Price", {"item_code":row.get("name"), "price_list":customer_price_list}, "price_list_rate")

		if stock_qty:
			#row["rate"] = item_rate or "0"
			row["rate"] = item_rate or "0"
		else:
			row["rate"] = ""

		row["stock_in_qty"] = stock_qty
		row["carton_qty"] = math.ceil(allow_carton_qty)

	path = 'bbt_bpm/bbt_bpm/page/customer_portal/customer_portal.html'
	html=frappe.render_template(path,{'data':items_data})
	return {'html':html}


def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("language"):conditions += " and book_language = '{0}'".format(filters.get('language'))
	elif filters.get("category"):conditions += " and item_group = '{0}'".format(filters.get('category'))
	elif filters.get("item_code"):conditions += " and name = '{0}'".format(filters.get('item_code'))
	elif filters.get("description"):conditions += " and description = '{0}'".format(filters.get('description'))
	elif filters.get("ratee"):conditions += " and rate = '{0}'".format(filters.get('ratee'))
	elif filters.get("stock_nos"):conditions += " and stock_in_qty = '{0}'".format(filters.get('stock_nos'))
	elif filters.get("stock_cartons"):conditions += " and carton_qty = '{0}'".format(filters.get('stock_cartons'))
	elif filters.get("books_carton"):conditions += " and no_of_items_can_be_packed = '{0}'".format(filters.get('books_carton'))
	# print(f'\n\n{conditions}\n\n')
	return conditions

def cart_page_condition(filters):
	conditions = "1=1"
	if filters.get("language"):conditions += " and language = '{0}'".format(filters.get('language'))
	elif filters.get("category"):conditions += " and item_group = '{0}'".format(filters.get('category'))
	elif filters.get("item_code"):conditions += " and item_code = '{0}'".format(filters.get('item_code'))
	elif filters.get("description"):conditions += " and description = '{0}'".format(filters.get('description'))
	elif filters.get("ratee"):conditions += " and rate = '{0}'".format(filters.get('ratee'))
	elif filters.get("stock_nos"):conditions += " and stock_in_qty = '{0}'".format(filters.get('stock_nos'))
	elif filters.get("stock_cartons"):conditions += " and carton_qty = '{0}'".format(filters.get('stock_cartons'))
	elif filters.get("books_carton"):conditions += " and book_per_carton = '{0}'".format(filters.get('books_carton'))
	# print(f'\n\n{conditions}\n\n')
	return conditions

@frappe.whitelist()
def add_to_cart_item(filters):
	data = json.loads(filters)
	order_qty = 0.0
	if not data.get("order_qty"):
		order_qty = flt(data.get("cartan_order_qty"))*flt(data.get("no_of_items_can_be_packed"))
	else:
		order_qty = flt(data.get("order_qty"))

	item = frappe.db.get_values("Item", {"name":data.get("item")}, ["item_name", "description", "item_group", "publisher"])
	
	added_item = frappe.db.get_values("Add To Cart Item", {"item_code":data.get("item"), "parent":frappe.session.user}, ["name", "ordered_qty_in_nos", "ordered_qty_in_cartons"], as_dict=1)

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
			"amount": flt(data.get("rate"))*flt(order_qty),
			"publisher": item[0][3]
		})
		doc.save(ignore_permissions=True)
	elif added_item:
		_cartons_qty = 0.0
		order_qty += flt(added_item[0].get("ordered_qty_in_nos"))
		_cartons_qty = flt(added_item[0].get("ordered_qty_in_cartons"))+flt(data.get("cartan_order_qty"))
		frappe.db.set_value("Add To Cart Item", {"name":added_item[0].get("name"), "item_code":data.get("item")}, {"ordered_qty_in_nos":order_qty, "ordered_qty_in_cartons":_cartons_qty})
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
			"amount": flt(data.get("rate"))*flt(order_qty),
			"publisher": item[0][3]
		})
		doc.save(ignore_permissions=True)
	return True

@frappe.whitelist()
def add_to_cart_details(user, filters):
	filters = json.loads(filters)
	#add_to_cart = frappe.db.sql("""SELECT name, item_code, item_group, description, rate, language, stock_in_nos, stock_in_cartons, book_per_carton, ordered_qty_in_nos, ordered_qty_in_cartons, amount from `tabAdd To Cart Item` where parent='{0}' """.format(user), as_dict=1)
	add_to_cart = frappe.db.sql("""SELECT name, item_code, item_group, description, rate, language, stock_in_nos, stock_in_cartons, book_per_carton, ordered_qty_in_nos, ordered_qty_in_cartons, amount, publisher from `tabAdd To Cart Item`  where parent='{0}' and {1} ORDER BY language""".format(user,cart_page_condition(filters)), as_dict=1)	
	add_qty =  frappe.db.sql("""SELECT sum(ordered_qty_in_nos) as total_ordered_qty, sum(ordered_qty_in_cartons) as total_cartons_qty, sum(amount) as total_amount from `tabAdd To Cart Item` where parent='{0}' """.format(user), as_dict=1)
	for row in add_to_cart:
		row["total_ordered_qty"] = add_qty[0].get("total_ordered_qty")
		row["total_cartons_qty"] = add_qty[0].get("total_cartons_qty")
		row["total_amount"] = add_qty[0].get("total_amount")

	cust = frappe.db.get_value("Customer", {"user":user}, "name")

	contact = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': cust, 'parenttype': 'Contact'}, fields=['parent'])
	# c_person = frappe.db.get_value('Contact', contact[0].parent)

	addresses = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': cust, 'parenttype': 'Address'}, fields=['parent'])
	# shipping_address = frappe.db.get_value('Address', addresses[0].parent, ['address_line1','city','country'])
	# billing_address = frappe.db.get_value('Address', addresses[1].parent, 'address_line1')

	path = 'bbt_bpm/bbt_bpm/page/customer_portal/add_to_cart.html'
	html=frappe.render_template(path,{'data':add_to_cart, 'contact': contact, 'addresses':addresses})
	return {'html':html}


@frappe.whitelist()
def new_order(client_feedback, contact_person, transportation_mode, preferred_transporter, freight_charges, delivery_type, shipping_address, billing_address, instruction_delivery, special_instruction):
	user = frappe.session.user
	data = frappe.db.sql("""SELECT item_code, item_name, item_group, description, rate, language, stock_in_nos, stock_in_cartons, book_per_carton, ordered_qty_in_nos, ordered_qty_in_cartons from `tabAdd To Cart Item` where publisher="BBT" and parent='{0}' """.format(user), as_dict=1)
	data2 = frappe.db.sql("""SELECT item_code, item_name, item_group, description, rate, language, stock_in_nos, stock_in_cartons, book_per_carton, ordered_qty_in_nos, ordered_qty_in_cartons from `tabAdd To Cart Item` where publisher="SRST" and parent='{0}' """.format(user), as_dict=1)
	data3 = frappe.db.sql("""SELECT item_code, item_name, item_group, description, rate, language, stock_in_nos, stock_in_cartons, book_per_carton, ordered_qty_in_nos, ordered_qty_in_cartons from `tabAdd To Cart Item` where item_group<>"Books" and parent='{0}' """.format(user), as_dict=1)
	customer = frappe.db.get_values("Customer", {"user":frappe.session.user}, ["name", "company", "default_currency", "default_price_list"])

	if frappe.db.get_value("Add To Cart", {"name":frappe.session.user}, "name") and customer and data:
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
		doc.contact_person = contact_person
		doc.mode_of_transport = transportation_mode
		doc.preferred_transporter = preferred_transporter
		doc.payment = freight_charges
		doc.delivery_type = delivery_type
		doc.shipping_address_name = shipping_address
		doc.customer_address =  billing_address
		doc.instruction_for_delivery = instruction_delivery
		doc.special_instruction = special_instruction
		doc.save()
		doc.add_comment('Comment', text=client_feedback)
		#frappe.delete_doc('Add To Cart', frappe.session.user)
		#frappe.db.commit()
		frappe.msgprint(_("Order Shall be processed Upon Approval"))
	if frappe.db.get_value("Add To Cart", {"name":frappe.session.user}, "name") and customer and data2:
		doc=frappe.new_doc("Sales Order")
		doc.customer = customer[0][0] if customer[0][0] else ""
		doc.company = "Sri Sri Sitaram Seva Trust" 
		doc.delivery_date = today()
		doc.currency = customer[0][2] if customer[0][2] else ""
		doc.selling_price_list = customer[0][3] if customer[0][3] else ""  
		for row in data2:
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
		doc.contact_person = contact_person
		doc.mode_of_transport = transportation_mode
		doc.preferred_transporter = preferred_transporter
		doc.payment = freight_charges
		doc.delivery_type = delivery_type
		doc.shipping_address_name = shipping_address
		doc.customer_address =  billing_address
		doc.instruction_for_delivery = instruction_delivery
		doc.special_instruction = special_instruction
		doc.save()
		doc.add_comment('Comment', text=client_feedback)
		#frappe.delete_doc('Add To Cart', frappe.session.user)
		#frappe.db.commit()
		frappe.msgprint(_("Order Shall be processed Upon Approval"))
	if frappe.db.get_value("Add To Cart", {"name":frappe.session.user}, "name") and customer and data3:
		doc=frappe.new_doc("Sales Order")
		doc.customer = customer[0][0] if customer[0][0] else ""
		doc.company = "Sri Sri Sitaram Seva Trust" 
		doc.delivery_date = today()
		doc.currency = customer[0][2] if customer[0][2] else ""
		doc.selling_price_list = customer[0][3] if customer[0][3] else ""  
		for row in data3:
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
		doc.contact_person = contact_person
		doc.mode_of_transport = transportation_mode
		doc.preferred_transporter = preferred_transporter
		doc.payment = freight_charges
		doc.delivery_type = delivery_type
		doc.shipping_address_name = shipping_address
		doc.customer_address =  billing_address
		doc.instruction_for_delivery = instruction_delivery
		doc.special_instruction = special_instruction
		doc.save()
		doc.add_comment('Comment', text=client_feedback)
		frappe.delete_doc('Add To Cart', frappe.session.user)
		frappe.db.commit()
		frappe.msgprint(_("Order Shall be processed Upon Approval"))

	frappe.delete_doc('Add To Cart', frappe.session.user)

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
	total_amount = frappe.db.sql("""SELECT sum(ordered_qty_in_nos) as total_ordered_qty, sum(ordered_qty_in_cartons) as total_cartons_qty, sum(amount) as amount From	`tabAdd To Cart Item` where parent = '{0}'""".format(frappe.session.user), as_dict=True)
	return total_amount


@frappe.whitelist()
def update_cartons_qty_on_cart(item, language, cartan_order_qty, rate, book_per_cartons):
	amount = 0.0
	order_qty = flt(book_per_cartons)*flt(cartan_order_qty)
	amount = flt(order_qty)*flt(rate)
	frappe.db.set_value("Add To Cart Item", {"item_code":item, "language":language}, {"ordered_qty_in_cartons":cartan_order_qty, "amount":amount, "ordered_qty_in_nos":order_qty})
	frappe.db.commit()
	total_amount = frappe.db.sql("""SELECT sum(ordered_qty_in_nos) as total_ordered_qty, sum(ordered_qty_in_cartons) as total_cartons_qty, sum(amount) as amount From	`tabAdd To Cart Item` where parent = '{0}'""".format(frappe.session.user), as_dict=True)
	total_amount.append(order_qty)
	return total_amount


@frappe.whitelist()
def create_doc(name):
	doc = frappe.new_doc("Issue")
	cust = frappe.db.get_values("Customer", {"user":frappe.session.user}, ["name", "company", "default_currency", "default_price_list"])
	doc.customer = cust[0][0]
	doc.item_name = name
	doc.insert(ignore_mandatory = True)
	
	return True

@frappe.whitelist(allow_guest=True)
def download_pdf(html, orientation="Landscape"):
	html2 = '<h1><img src="/files/BBT Letterhead.PNG" style="width: 100%;"></h1>'
    #html3 = '<html><head><script>var dt = new Date(); document.getElementById('date-time').innerHTML=dt;</script></head><body><p><span id='date-time'></span></p></body></html>'
	html=html2+now()+'<p><br></p>'+html
	frappe.local.response.filename = "report.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": orientation,'page-size':'A4'})
	frappe.local.response.type = "download"
	

@frappe.whitelist()
def get_pdf_data(filters):
	filters = json.loads(filters)
	items_data = frappe.db.sql("""SELECT name, item_group, description, no_of_items_can_be_packed, carton, book_language,publisher from `tabItem` where {0} """.format(get_filters_codition(filters)), as_dict=1)
		
	for row in items_data:
		item_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("name")), as_dict=1)
		carton_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("carton")), as_dict=1)

		item_reserved_qty = frappe.db.sql("""SELECT item_code, sum(qty) as qty From `tabStock Blocking Unblocking Table` where item_code='{0}' """.format(row.get("name")), as_dict=1)
		cartons_reserved_qty = frappe.db.sql("""SELECT sum(qty) as qty From `tabStock Blocking Unblocking Table` where item_code='{0}' """.format(row.get("carton")), as_dict=1)
		
		stock_qty=0.0
		if item_qty[0] and item_reserved_qty[0]:
			stock_qty = abs(flt(item_qty[0].get("actual_qty"))-flt(item_reserved_qty[0].get("qty")))
		else:
			stock_qty=item_qty[0].get("actual_qty") if item_qty[0] else 0
		cartons_qty = 0.0
		if carton_qty[0] and cartons_reserved_qty[0]:
			cartons_qty = abs(flt(carton_qty[0].get("actual_qty"))-flt(cartons_reserved_qty[0].get("qty")))
		else:
			cartons_qty=carton_qty[0].get("actual_qty") if carton_qty[0] else 0

		allow_carton_qty = 0.0
		if row.get("no_of_items_can_be_packed"):
			allow_carton_qty = flt(stock_qty)/flt(row.get("no_of_items_can_be_packed"))
		
		customer_user = frappe.session.user
		customer_price_list = frappe.db.get_value("Customer", {"user":customer_user}, "default_price_list")
		item_rate = frappe.db.get_value("Item Price", {"item_code":row.get("name"), "price_list":customer_price_list}, "price_list_rate")

		if stock_qty:
			#row["rate"] = item_rate or "0"
			row["rate"] = item_rate or "0"
		else:
			row["rate"] = ""

		row["stock_in_qty"] = stock_qty
		row["carton_qty"] = math.ceil(allow_carton_qty)

	path = 'bbt_bpm/bbt_bpm/page/customer_portal/pdf.html'
	html=frappe.render_template(path,{'data':items_data})
	return {'html':html}


# @frappe.whitelist()
# def new_address(user):
# 	doc = frappe.new_doc("Address")
# 	cust_name = frappe.db.get_value("Customer", {"user":user}, "name")
# 	address_link_dT = frappe.get_all('Dynamic Link', filters={'link_name': cust_name, 'parenttype': 'Address'}, fields=['link_doctype'])[0]['link_doctype']

	
# 	# doc.address_title = 'abc'
# 	# doc.pincode = 'xyz'
# 	# doc.address_line1 = 'edfed'
# 	# doc.city = 'Pune'

# 	# for l in doc.links:  WILL NOT WORK AS doc IS ADDRESS OBJECT AND NOT DOCUMENT
# 	# 	l.link_doctype = address_link_dT
# 	# 	l.link_name =  cust_name

# 	# doc.user = frappe.session.user
# 	doc.append("links", {
# 		"link_doctype": address_link_dT,
# 		"link_name": cust_name
# 	})

		
# 	# doc.save(ignore_permissions=True)
# 	# doc.save()
# 	# doc.insert(ignore_mandatory = True, ignore_permissions=True)
# 	#doc.save(ignore_permissions=True)
	
# 	return True

# @frappe.whitelist()
# def new_contact(user):
# 	doc = frappe.new_doc("Contact")
# 	cust_name = frappe.db.get_value("Customer", {"user":user}, "name")
# 	contact_link_dT = frappe.get_all('Dynamic Link', filters={'link_name': cust_name, 'parenttype': 'Contact'}, fields=['link_doctype'])[0]['link_doctype']

# 	doc.append("links", {
# 		"link_doctype": contact_link_dT,
# 		"link_name": cust_name
# 	})

# 	doc.insert(ignore_mandatory = True, ignore_permissions=True)
	
# 	return True
