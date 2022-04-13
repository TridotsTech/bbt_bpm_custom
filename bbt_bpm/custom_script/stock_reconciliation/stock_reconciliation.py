import frappe
from erpnext.stock.utils import get_stock_balance

@frappe.whitelist()
def get_warehouse_data(warehouse, company, posting_date, posting_time,item_code=None,book_language=None):
	print('\n\n\nPosting date\n\n', posting_date)
	print('\n\n\nPosting time\n\n', posting_time)
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
								 """, (lft, rgt, company))

	res = []
	for d in set(wh_data):
		stock_bal = get_stock_balance(d[0], d[2], posting_date, posting_time,
			 with_valuation_rate=True)
		f_item_code,disabled,f_book_language = frappe.db.get_value("Item", d[0], ["item_code","disabled","book_language"])
		if disabled == 0:
			if item_code and not book_language:
				if(f_item_code == item_code):
					res.append({
						"item_code": d[0],
						"warehouse": d[2],
						"qty": stock_bal[0],
						"item_name": d[1],
						"valuation_rate": stock_bal[1],
						"current_qty": stock_bal[0],
						"current_valuation_rate": stock_bal[1]
					})
			elif book_language and not item_code:
				if(f_book_language == book_language):
					res.append({
						"item_code": d[0],
						"warehouse": d[2],
						"qty": stock_bal[0],
						"item_name": d[1],
						"valuation_rate": stock_bal[1],
						"current_qty": stock_bal[0],
						"current_valuation_rate": stock_bal[1]
					})
			elif item_code and book_language:
				if(f_item_code == item_code and f_book_language == book_language):
					res.append({
						"item_code": d[0],
						"warehouse": d[2],
						"qty": stock_bal[0],
						"item_name": d[1],
						"valuation_rate": stock_bal[1],
						"current_qty": stock_bal[0],
						"current_valuation_rate": stock_bal[1]
					})
			else:
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

