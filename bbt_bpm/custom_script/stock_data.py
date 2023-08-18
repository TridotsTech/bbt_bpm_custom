import json
import frappe


@frappe.whitelist()
def stock_data():
	req_data = json.loads(frappe.request.data)
	warehouse = req_data.get('warehouse')
	prices_list = req_data.get('price_list')
	all_data = []

	for pl in prices_list:
		data = frappe.db.sql("""
		SELECT sum(BN.actual_qty) as actual_qty,BN.item_name as item_name,BN.item_code as item_code,IP.price_list as price_list,IP.price_list_rate as price_list_rate from `tabBin` as BN INNER JOIN `tabItem Price` AS IP ON BN.item_code = IP.item_code where BN.warehouse='{0}' and IP.price_list = "{1}" group by BN.item_code""".format(warehouse,pl), as_dict=True)
		
		for row in data:
			existing_item = next((item for item in all_data if item["item_code"] == row["item_code"]), None)
			if existing_item:
				existing_item["price_list"][row["price_list"]] = row["price_list_rate"]
			else:
				item_data = {
				"actual_qty": row["actual_qty"],
				"item_name": row["item_name"],
				"item_code": row["item_code"],
				"price_list": {row["price_list"]: row["price_list_rate"]}
				}
				all_data.append(item_data)

	return all_data