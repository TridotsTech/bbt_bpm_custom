from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def map_on_stock_entry(source_name, target_doc=None):
	target_doc = get_mapped_doc("Quotation", source_name,
		{"Quotation": {
		"doctype": "Stock Entry",
		"field_map": {
			"company": "company",
			}
		},
		"Quotation Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"warehouse": "s_warehouse",
			},
		}
	})
	return target_doc