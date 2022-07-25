import frappe

@frappe.whitelist()
def contact_links(user):
	# doc = frappe.get_doc('Address', name)
	cust_name = frappe.db.get_value("Customer", {"user":user}, "name")
	contact_link_dT = frappe.get_all('Dynamic Link', filters={'link_name': cust_name, 'parenttype': 'Contact'}, fields=['link_doctype'])[0]['link_doctype']

	return contact_link_dT, cust_name