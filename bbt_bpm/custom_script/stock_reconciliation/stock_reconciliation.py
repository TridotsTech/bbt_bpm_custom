# import frappe
# from erpnext.stock.utils import get_stock_balance
# from frappe.utils import cint, cstr, flt

# # @frappe.whitelist()
# # def get_data(warehouse, company, posting_date, posting_time, item_code=None, qty=None):

# # 	items = [frappe._dict({
# # 		#'book_language': book_language,
# # 		'qty': qty,
# # 		'item_code': item_code,
# # 		'warehouse': warehouse
# # 	})]

# # 	if not item_code and not qty:
# # 		items = get_warehouse_data(warehouse, company, posting_date, posting_time)

# # 	res = []
# # 	itemwise_batch_data = get_itemwise_batch(warehouse, posting_date, company, item_code, qty)

# # 	for d in items:
# # 		if d.item_code in itemwise_batch_data:
# # 			valuation_rate = get_stock_balance(d.item_code, d.warehouse,
# # 				posting_date, posting_time, with_valuation_rate=True)[1]
# # 			print('///////////////')
# # 			print("\n\n\n\n Valuation Rate",valuation_rate)
# # 			print('///////////////')

# # 			for row in itemwise_batch_data.get(d.item_code):
# # 				if not row.qty:
# # 					continue

# # 				args = get_item_data(row, row.qty, valuation_rate)
# # 				res.append(args)
# # 		else:
# # 			stock_bal = get_stock_balance(d.item_code, d.warehouse, posting_date, posting_time, with_valuation_rate=True , with_serial_no=cint(d.has_serial_no))
# # 			print('///////////////')
# # 			print("\n\n\n\n stock bal - \n\n",stock_bal)
# # 			print('///////////////')

# # 			qty, valuation_rate, serial_no = stock_bal[0], stock_bal[1], stock_bal[2] if cint(d.has_serial_no) else ''

# # 			if not stock_bal[0]:
# # 					continue

# # 			args = get_item_data(d, qty, valuation_rate, serial_no)

# # 			print('///////////////')
# # 			print("\n\n\n\n Args - \n\n",args)
# # 			print('///////////////')


# # 			res.append(args)
# # 			print('///////////////')
# # 			print("\n\n\n\n Res - \n\n",res)
# # 			print('///////////////')

# # 	return res


# @frappe.whitelist()
# def get_warehouse_data(warehouse, company, posting_date, posting_time):
# 	lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
# 	wh_data = frappe.db.sql("""SELECT i.name, i.item_name, bin.warehouse FROM `tabBin` bin, `tabItem` i
# 							   WHERE i.name = bin.item_code  and i.disabled=0 and i.is_stock_item = 1
# 							   and i.has_variants = 0 and i.has_serial_no = 0 and i.has_batch_no = 0
# 							   and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=bin.warehouse)
# 								""", (lft, rgt))

# 	wh_data += frappe.db.sql(""" SELECT i.name, i.item_name, id.default_warehouse
# 								 FROM `tabItem` i, `tabItem Default` id
# 								 WHERE i.name = id.parent
# 								 and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=id.default_warehouse)
# 								 and i.is_stock_item = 1 and i.has_serial_no = 0 and i.has_batch_no = 0
# 								 and i.has_variants = 0 and i.disabled = 0 and id.company=%s
# 								 group by i.name
# 								 """, (lft, rgt, company))

# 	res = []
# 	for d in set(wh_data):
# 		stock_bal = get_stock_balance(d[0], d[2], posting_date, posting_time,
# 			 with_valuation_rate=True)

# 		if frappe.db.get_value("Item", d[0], "disabled") == 0:
# 			res.append({
# 				"item_code": d[0],
# 				"warehouse": d[2],
# 				"qty": stock_bal[0],
# 				"item_name": d[1],
# 				"valuation_rate": stock_bal[1],
# 				"current_qty": stock_bal[0],
# 				"current_valuation_rate": stock_bal[1]
# 			})

# 	return res

# # def get_itemwise_batch(warehouse, posting_date, company, item_code=None, book_language=None, qty=None):
# # 	from erpnext.stock.report.batch_wise_balance_history.batch_wise_balance_history import execute
# # 	itemwise_batch_data = {}

# # 	filters = frappe._dict({
# # 		'warehouse': warehouse,
# # 		'from_date': posting_date,
# # 		'to_date': posting_date,
# # 		'company': company
# # 	})

# # 	if item_code:
# # 		filters.item_code = item_code

# # 	columns, data = execute(filters)

# # 	for row in data:
# # 		itemwise_batch_data.setdefault(row[0], []).append(frappe._dict({
# # 			'item_code': row[0],
# # 			'warehouse': warehouse,
# # 			'qty': row[8],
# # 			'item_name': row[1],
# # 			'batch_no': row[4]
# # 		}))

# # 	return itemwise_batch_data

# # def get_item_data(row, qty, valuation_rate, serial_no=None):
# # 	return {
# # 		'item_code': row.item_code,
# # 		'warehouse': row.warehouse,
# # 		'qty': qty,
# # 		'item_name': row.item_name,
# # 		'valuation_rate': valuation_rate,
# # 		'current_qty': qty,
# # 		'current_valuation_rate': valuation_rate,
# # 		'current_serial_no': serial_no,
# # 		'serial_no': serial_no,
# # 		'batch_no': row.get('batch_no')
# # 	}


import frappe
from erpnext.stock.utils import get_stock_balance

@frappe.whitelist()
def get_warehouse_data(warehouse, company, posting_date, posting_time,item_code=None, book_language=None):
	lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
	wh_data = frappe.db.sql("""SELECT i.name, i.item_name, bin.warehouse, i.book_language FROM `tabBin` bin, `tabItem` i
							   WHERE i.name = bin.item_code  and i.disabled=0 and i.is_stock_item = 1
							   and i.has_variants = 0 and i.has_serial_no = 0 and i.has_batch_no = 0
							   and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=bin.warehouse)
								""", (lft, rgt))

	wh_data += frappe.db.sql(""" SELECT i.name, i.item_name, id.default_warehouse, i.book_language
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

		# Check if document is enabled ie; disabled field is unchecked(condition true)
		if frappe.db.get_value("Item", d[0], "disabled") == 0:
			if item_code:
				if(d[0] == item_code):
					res.append({
						"item_code": d[0],
						"warehouse": d[2],
						"qty": stock_bal[0],
						"item_name": d[1],
						"valuation_rate": stock_bal[1],
						"current_qty": stock_bal[0],
						"current_valuation_rate": stock_bal[1]
					})
			elif book_language:
				if(d[3] == book_language):
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

