import json
import frappe


@frappe.whitelist()
def stock_data():
	req_data = json.loads(frappe.request.data)
	warehouse = req_data.get('warehouse')
	prices_list = req_data.get('price_list')
	all_data = []

	for pl in prices_list:
		print(pl)
		data = frappe.db.sql("""
		SELECT sum(BN.actual_qty) as actual_qty,BN.item_name as item_name,BN.item_code as item_code,IP.price_list as price_list from `tabBin` as BN INNER JOIN `tabItem Price` AS IP ON BN.item_code = IP.item_code where BN.warehouse='{0}' and IP.price_list = "{1}" group by BN.item_code""".format(warehouse,pl), as_dict=True)
		
		print(data)
		all_data.extend(data)

	return all_data