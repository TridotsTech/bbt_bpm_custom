from __future__ import unicode_literals
from re import sub
import frappe
from frappe.utils import cint, cstr,flt
import json
from frappe.model.mapper import get_mapped_doc
import math
import re
from frappe import _, msgprint, scrub
from frappe.utils import has_common
from datetime import date


def validate(doc, method=None):
	pass

def after_insert(doc, method):
	if doc.user_type == "Website User":
		roles = ["Customer User", "Customer"]
		for role in roles:
			doc.append("roles", {
						    "owner": "Administrator",
						    "modified_by": "Administrator",
						    "parent": doc.name,
						    "parentfield": "roles",
						    "parenttype": "User",
						    "docstatus": 0,
						    "role": role,
						    "doctype": "Has Role"
						})
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		try:
			cust_doc = frappe.new_doc("Customer")
			cust_doc.customer_name = doc.full_name
			cust_doc.customer_group = "Retail"
			cust_doc.territory = "All Territories"
			cust_doc.user = doc.name
			cust_doc.default_price_list = "Web Price"
			cust_doc.save(ignore_permissions=True)
			frappe.db.commit()
		except Exception as e:
			pass
	

