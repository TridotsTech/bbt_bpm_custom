from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json


def on_submit(doc, method=None):
	sales_order = []
	for row in doc.items:
		sales_order.append(row.sales_order)

	if sales_order:
		pick_list = frappe.db.sql("""SELECT distinct parent from `tabPick List Item` where sales_order='{0}' and docstatus=1 """.format(sales_order[0]), as_list=1)

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