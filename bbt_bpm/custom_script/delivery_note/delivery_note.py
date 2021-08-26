from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math


def on_submit(doc, method):
	for row in doc.items:
		item_qty = frappe.db.get_value("Item", {"name":row.item_code}, "goods_in_transit")	
		goods_in_transit = flt(item_qty)+flt(row.qty)
		frappe.db.set_value("Item", row.item_code, "goods_in_transit", goods_in_transit)


def on_update_after_submit(doc, method):
	if doc.delivered:
		for row in doc.items:
			item_qty = frappe.db.get_value("Item", {"name":row.item_code}, "goods_in_transit")	
			goods_in_transit = flt(item_qty)-flt(row.qty)
			frappe.db.set_value("Item", row.item_code, "goods_in_transit", goods_in_transit)


def save(doc, method):
	set_items(doc)


def set_items(doc):
	for item in doc.items:
		is_packaging_item = frappe.db.get_value("Item", item.item_code, "no_of_items_can_be_packed")
		is_carton_req = frappe.db.get_value("Item", item.item_code, "carton")
		item_weight = frappe.db.get_value("Item", item.item_code, "weight_per_unit")
		available_qty = frappe.db.sql_list("""select sum(actual_qty) from tabBin 
							where item_code='{0}'""".format(item.item_code))
		if is_packaging_item and is_carton_req:
			carton_item_doc = frappe.get_cached_doc("Item", {"item_code": is_carton_req})
			qty = item.qty / is_packaging_item
			# set values below
			doc.carton_qty = math.ceil(qty)
			doc.carton_no = carton_item_doc.item_name
			doc.per_carton_weight = carton_item_doc.per_carton_weight_kgs
			doc.available_stock = available_qty[0]
			doc.used_qty = item.qty
			doc.total_carton_weight = item_weight * item.qty + doc.per_carton_weight * doc.carton_qty
			doc.dimension = carton_item_doc.dimension
		elif not is_packaging_item:
			item_link = "<a target=_blank href='#Form/Item/{0}'>{1}</a>".format(item.item_code, item.item_code)
			msg = "Kindly Update No. of Item can be packed Field for Item {0}".format(item_link)
			frappe.throw(msg)