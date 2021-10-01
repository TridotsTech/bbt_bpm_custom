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
	# if has_common(["Customer"], frappe.get_roles(doc.name)):
	# 	cust_doc = frappe.new_doc("Customer")
	# 	cust_doc.customer_name = doc.full_name
	# 	cust_doc.customer_group = "Retail"
	# 	cust_doc.territory = "All Territories"
	# 	cust_doc.user = doc.name
	# 	cust_doc.save()
	# 	frappe.db.commit()

def after_insert(doc, method):
	if has_common(["Customer"], frappe.get_roles(doc.name)):
		doc.add_roles("Customer User")
		doc.save()
		cust_doc = frappe.new_doc("Customer")
		cust_doc.customer_name = doc.full_name
		cust_doc.customer_group = "Retail"
		cust_doc.territory = "All Territories"
		cust_doc.user = doc.name
		cust_doc.save()
		frappe.db.commit()

