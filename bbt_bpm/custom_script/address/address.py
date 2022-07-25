from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math
from frappe import _, msgprint, scrub
from frappe.utils import has_common
from datetime import date

@frappe.whitelist()
def address_links(user):
	# doc = frappe.get_doc('Address', name)
	cust_name = frappe.db.get_value("Customer", {"user":user}, "name")
	address_link_dT = frappe.get_all('Dynamic Link', filters={'link_name': cust_name, 'parenttype': 'Address'}, fields=['link_doctype'])[0]['link_doctype']

	return address_link_dT, cust_name
#------------------------------------------------------------------
#Permission Query
#------------------------------------------------------------------
def add_get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	cust = frappe.db.get_value("Customer", {"user":user}, "name")
	address=frappe.db.sql("""select parent from `tabDynamic Link` where link_name='{0}' """.format(cust), as_dict=1)
	add_list = [ '"%s"'%add.get("parent") for add in address ]

	roles = frappe.get_roles();
	if user != "Administrator" and has_common(['Customer'],roles) :
		if add_list:
			return """(`tabAddress`.name in ({0}) )""".format(','.join(add_list))
		else:
			# return "1=2"
			return """(`tabAddress`.name is null)"""