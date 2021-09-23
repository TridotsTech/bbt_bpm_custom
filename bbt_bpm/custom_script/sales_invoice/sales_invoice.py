from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math


def on_submit(doc, method=None):
	sales_order = []
	for row in doc.items:
		sales_order.append(row.sales_order)

	if sales_order:
		pick_list = frappe.db.sql("""SELECT distinct parent from `tabPick List Item` where sales_order='{0}' 
									and docstatus=1 """.format(sales_order[0]), as_list=1)

		if pick_list:
			for row in pick_list:
				doc.pick_list_ref = row[0]
				pick_doc = frappe.get_doc("Pick List", row[0])
				pick_doc.append("sales_invoice", {
						"sales_invoice":doc.name,
						"parent":row[0]
					})
				pick_doc.flags.ignore_validate_update_after_submit = True
				pick_doc.save()
				frappe.db.commit()


def save(doc, method):
	set_items(doc)


def set_items(doc):
	for item in doc.items:
		is_packaging_item = frappe.db.get_value("Item", item.item_code, "no_of_items_can_be_packed")
		is_carton_req = frappe.db.get_value("Item", item.item_code, "carton")
		available_qty = frappe.db.sql_list("""select sum(actual_qty) from tabBin 
									where item_code='{0}'""".format(item.item_code))
		if is_packaging_item and is_carton_req:
			carton_item_doc = frappe.get_cached_doc("Item", {"item_code": is_carton_req})
			item.available_stock = available_qty[0]
			item.dimension = carton_item_doc.dimension
			item.used_qty = item.qty
