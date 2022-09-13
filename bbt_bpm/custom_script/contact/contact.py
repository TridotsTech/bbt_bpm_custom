import frappe

@frappe.whitelist()
def contact_links(user):
	# doc = frappe.get_doc('Address', name)
	cust_name = frappe.db.get_value("Customer", {"user":user}, "name")
	contact_link = frappe.get_all('Dynamic Link', filters={'link_name': cust_name, 'parenttype': 'Contact'}, fields=['link_doctype'])

	if contact_link: 
		return contact_link[0]['link_doctype'], cust_name