from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cstr, cint
from frappe import _, msgprint, scrub
from frappe.model.naming import make_autoname
from frappe.utils import has_common
from datetime import date



#------------------------------------------------------------------
#Permission Query
#------------------------------------------------------------------
def cust_get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	cust_list = []
	cust=frappe.db.sql("""select name from `tabCustomer` where user='{0}' """.format(frappe.session.user), as_dict=1) 
	cust_list = [ '"%s"'%c.get("name") for c in cust ]

	roles = frappe.get_roles();
	if user != "Administrator" and has_common(['Customer'],roles) :
		if cust_list:
			return """(`tabCustomer`.name in ({0}) )""".format(','.join(cust_list))
		else:
			return """(`tabCustomer`.name!='1')"""