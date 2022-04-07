import frappe
from erpnext.stock.utils import get_stock_balance

@frappe.whitelist()
def get_warehouse_data(warehouse, company, posting_date, posting_time, item_code, book_language, qty):
	lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
	wh_data = frappe.db.sql("""SELECT i.name, i.item_name, bin.warehouse FROM `tabBin` bin, `tabItem` i
							   WHERE i.name = bin.item_code  and i.disabled=0 and i.is_stock_item = 1
							   and i.has_variants = 0 and i.has_serial_no = 0 and i.has_batch_no = 0
							   and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=bin.warehouse)
								""", (lft, rgt))

	wh_data += frappe.db.sql(""" SELECT i.name, i.item_name, id.default_warehouse
								 FROM `tabItem` i, `tabItem Default` id
								 WHERE i.name = id.parent
								 and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=id.default_warehouse)
								 and i.is_stock_item = 1 and i.has_serial_no = 0 and i.has_batch_no = 0
								 and i.has_variants = 0 and i.disabled = 0 and id.company=%s
								 group by i.name
								 """, (lft, rgt, company, item_code, book_language, qty))

	res = []
	for d in set(wh_data):
		stock_bal = get_stock_balance(d[0], d[2], posting_date, posting_time,
			 with_valuation_rate=True)

		if frappe.db.get_value("Item", d[0], "disabled") == 0:
			res.append({
				"item_code": d[0],
				"warehouse": d[2],
				"qty": stock_bal[0],
				"item_name": d[1],
				"valuation_rate": stock_bal[1],
				"current_qty": stock_bal[0],
				"current_valuation_rate": stock_bal[1]
			})

	return res

