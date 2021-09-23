from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json



def on_submit(doc, method):
	frappe.db.set_value("Sales Order", doc.sales_order_ref, "stock_transfer_ref", doc.name)
	frappe.db.set_value("Sales Order Item", {"parent":doc.sales_order_ref}, "warehouse", doc.to_warehouse)
	frappe.db.set_value('Sales Order', doc.sales_order_ref, "set_warehouse", doc.to_warehouse)
	if doc.sales_order_ref or doc.quotation_ref:
		stock_block = frappe.new_doc("Stock Blocking Unblocking")
		stock_block.stock_block_unblock = doc.name
		stock_block.sales_order = doc.sales_order_ref
		stock_block.quotation = doc.quotation_ref

		for row in doc.items:
			stock_block.append("items", {
				"source_warehouse": row.s_warehouse,
				"target_warehouse": row.t_warehouse,
				"item_code": row.item_code,
				"item_name": row.item_name,
				"qty": row.qty,
				"uom": row.uom,
				"rate": row.basic_rate,
				"amount": row.amount 
			})
		
		
		stock_block.insert()
		stock_block.save()
		frappe.db.commit()


def on_cancel(doc, method):
	frappe.db.set_value("Sales Order", doc.sales_order_ref, "stock_transfer_ref", "")
	frappe.db.set_value("Sales Order Item", {"parent":doc.sales_order_ref}, "warehouse", doc.from_warehouse)
	frappe.db.sql("""delete from `tabStock Blocking Unblocking` where name='{0}'""".format(doc.name))
	frappe.db.commit()
