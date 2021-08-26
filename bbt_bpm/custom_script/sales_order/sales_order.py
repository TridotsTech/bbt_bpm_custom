from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
from frappe.model.mapper import get_mapped_doc


def validate(doc, method):
	for row in doc.items:
		doc.stock_transfer_ref=frappe.db.get_value("Stock Entry", {"quotation_ref":row.prevdoc_docname, "docstatus":1}, "name")	
		outstanding_amount = frappe.db.sql("""SELECT sum(outstanding_amount) as amount from `tabSales Invoice` where customer='{0}' and company='{1}' and docstatus=1 """.format(doc.customer, doc.company), as_dict=1)
		if outstanding_amount[0]:
			doc.outstanding_amount = outstanding_amount[0].get('amount') 

@frappe.whitelist()
def map_on_stock_entry(source_name, target_doc=None):
	stock_entry_types="Stock Reservation"
	target_doc = get_mapped_doc("Sales Order", source_name,
		{"Sales Order": {
		"doctype": "Stock Entry",
		"field_map": {
			"company": "company",
			"name": "sales_order_ref",
			"set_warehouse": "from_warehouse",
			"stock_entry_type": "Stock Reservation"
			}
		},
		"Sales Order Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"warehouse": "s_warehouse",
				"transfer_qty": "qty",
			},
		}
	})
	return target_doc

