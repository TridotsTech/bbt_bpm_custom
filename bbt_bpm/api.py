import frappe

#def before_save(doc, method):

@frappe.whitelist()
def get_item_code_data(item_code):

	ic_data = frappe.db.sql(f""" SELECT item_code, warehouse, qty, valuation_rate, qty_in_cartons, batch_no, physical_qty, quantity_difference
							 FROM `tabStock Reconciliation Item` 
							 WHERE item_code='{item_code}' """, as_dict=True )
	return ic_data


@frappe.whitelist()
def get_warehouse_data(warehouse):

	wh_data = frappe.db.sql(f""" SELECT item_code, warehouse, qty, valuation_rate, qty_in_cartons, batch_no, physical_qty, quantity_difference
							 FROM `tabStock Reconciliation Item` 
							 WHERE warehouse='{warehouse}' """, as_dict=True )
	return wh_data

@frappe.whitelist()
def get_language_data(book_language):

	bl_data = frappe.db.sql(f""" SELECT item_code, warehouse, qty, valuation_rate, qty_in_cartons, batch_no, physical_qty, quantity_difference
							 FROM `tabStock Reconciliation Item` 
							 WHERE warehouse='{book_language}' """, as_dict=True )
	return bl_data

@frappe.whitelist()
def get_quantity_data(book_language):

	bl_data = frappe.db.sql(f""" SELECT item_code, warehouse, qty, valuation_rate, qty_in_cartons, batch_no, physical_qty, quantity_difference
							 FROM `tabStock Reconciliation Item` 
							 WHERE warehouse='{book_language}' """, as_dict=True )
	return bl_data