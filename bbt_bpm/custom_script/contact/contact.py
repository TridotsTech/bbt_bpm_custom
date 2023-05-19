import frappe
from frappe.utils import has_common
from frappe.model.naming import make_autoname
from frappe.utils import cstr, has_gravatar, cint




def validate(doc,method):
	new_name = doc.first_name + " " + doc.middle_name + " " + doc.last_name
	print(new_name)
	# return frappe.rename_doc("Contact", 
	# 	doc.name, 
	# 	new_name, 
	# 	force=False,
	# 	)


@frappe.whitelist()
def contact_links(user):
	# doc = frappe.get_doc('Address', name)
	cust_name = frappe.db.get_value("Customer", {"user":user}, "name")
	contact_link = frappe.get_all('Dynamic Link', filters={'link_name': cust_name, 'parenttype': 'Contact'}, fields=['link_doctype'])

	if not contact_link: 
		# print(frappe.get_roles(user))  ['Customer', 'Customer User', 'All', 'Guest']
		return 'Customer', cust_name

	return contact_link[0]['link_doctype'], cust_name


#------------------------------------------------------------------
#Permission Query
#------------------------------------------------------------------

def add_get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	cust = frappe.db.get_value("Customer", {"user":user}, "name")
	contact = frappe.db.sql("""select parent from `tabDynamic Link` where link_name ='{0}' """.format(cust), as_dict=1)

	con_list = [ '"%s"'%con.get("parent") for con in contact ]

	roles = frappe.get_roles();
	if user != "Administrator" and has_common(['Customer'],roles) :
		if con_list:
			return """(`tabContact`.name in ({0}) )""".format(','.join(con_list))
		else:
			# return "1=2"
			return """(`tabContact`.name is null)"""