import frappe


def validate(doc,method):
	item_name = frappe.db.get_value("Item",{"item_code":doc.item_code},"item_name")
	doc.item_name = item_name
