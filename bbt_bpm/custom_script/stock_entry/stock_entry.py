from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json

def on_submit(doc, method):
	frappe.db.set_value("Sales Order", doc.sales_order_ref, "stock_transfer_ref", doc.name)


def on_cancel(doc, method):
	frappe.db.set_value("Sales Order", doc.sales_order_ref, "stock_transfer_ref", "")