from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json


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

