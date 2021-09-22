# Copyright (c) 2013, Ashish and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data



def get_data(filters):
	data = []
	query_data = frappe.db.sql("""SELECT DISTINCT
								itm.name, 
								itm.item_code, 
								itm.description
								
							FROM 
								tabItem itm"""
							,as_dict=True)

	for row in query_data:
		data_row = {}
		
		so_details = frappe.db.sql(""" SELECT so.company from `tabSales Order` so JOIN `tabSales Order Item` soi on
		 so.name=soi.parent where item_code=%(item_code)s and so.docstatus=1 """, 
		 {"item_code":row.item_code}, as_dict = 1)
		
		
		if so_details:
			data_row["company"]=so_details[0].get("company")
		else:
			data_row["company"]= None
		
		item_warehouses = frappe.db.sql_list(""" SELECT DISTINCT warehouse from tabBin 
		where item_code=%(item_code)s and actual_qty>0""", {"item_code":row.item_code})
		data_row["item_code"] = row.item_code
		data_row["description"] = row.description


		for warehouse in item_warehouses:	
			update_row = data_row.copy()
			item_available_qty = frappe.db.sql(""" SELECT sum(actual_qty) as available_stock, date(modified) as last_stock_updated_date FROM `tabBin` WHERE
			item_code=%(item_code)s and warehouse=%(warehouse)s """, {"item_code":row.item_code, "warehouse":warehouse}, as_dict = 1)
			update_row["warehouse"] = warehouse
			update_row["available_stock"] = item_available_qty[0].get("available_stock")
			update_row["last_received_date"] = item_available_qty[0].get("last_stock_updated_date")

			last_stock_updated_date = frappe.db.sql(""" SELECT  date(modified) as last_stock_updated_date FROM `tabStock Ledger Entry` WHERE
			item_code=%(item_code)s and warehouse=%(warehouse)s """, {"item_code":row.item_code, "warehouse":warehouse}, as_dict = 1)
			update_row["last_stock_updated_date"] = last_stock_updated_date[0].get("last_stock_updated_date")

			last_issued_date = frappe.db.sql_list(""" SELECT  date(posting_date) as last_issued_date FROM `tabSales Invoice` so left JOIN 
			`tabSales Invoice Item` soi on so.name=soi.parent WHERE soi.item_code=%(item_code)s and soi.warehouse=%(warehouse)s """, {"item_code":row.item_code, "warehouse":warehouse})
			
			if last_issued_date:
				update_row["last_issued_date"] = last_issued_date[-1]
			else:
				update_row["last_issued_date"] = None

			six_month_quantity = frappe.db.sql_list(""" SELECT sum(soi.qty) as six_month_qty from `tabSales Invoice Item` soi
			join `tabSales Invoice` so on so.name=soi.parent and so.posting_date between DATE_ADD(CURDATE(), INTERVAL -6 MONTH)
			and CURDATE() where item_code=%(item_code)s """, {"item_code":row["item_code"]})
			update_row["six_month_qty"] = six_month_quantity[0]

			twelve_month_quantity = frappe.db.sql_list(""" SELECT sum(soi.qty) as six_month_qty from `tabSales Invoice Item` soi
			join `tabSales Invoice` so on so.name=soi.parent and so.posting_date between DATE_ADD(CURDATE(), INTERVAL -6 MONTH) 
			and DATE_ADD(CURDATE(), INTERVAL -12 MONTH) where item_code=%(item_code)s """, {"item_code":row["item_code"]})
			update_row["twelve_month_qty"] = twelve_month_quantity[0]

			eighteen_month_quantity = frappe.db.sql_list(""" SELECT sum(soi.qty) as six_month_qty from `tabSales Invoice Item` soi
			join `tabSales Invoice` so on so.name=soi.parent and so.posting_date between DATE_ADD(CURDATE(), INTERVAL -12 MONTH) 
			and DATE_ADD(CURDATE(), INTERVAL -18 MONTH) where item_code=%(item_code)s """, {"item_code":row["item_code"]})
			update_row["eighteen_month_qty"] = eighteen_month_quantity[0]

			twenty_four_month_quantity = frappe.db.sql_list(""" SELECT sum(soi.qty) as six_month_qty from `tabSales Invoice Item` soi
			join `tabSales Invoice` so on so.name=soi.parent and so.posting_date between DATE_ADD(CURDATE(), INTERVAL -18 MONTH) 
			and DATE_ADD(CURDATE(), INTERVAL -24 MONTH) where item_code=%(item_code)s """, {"item_code":row["item_code"]})
			update_row["twenty_four_month_qty"] = twenty_four_month_quantity[0]

			above_twenty_four_month_quantity = frappe.db.sql_list(""" SELECT sum(soi.qty) as six_month_qty from `tabSales Invoice Item` soi
			join `tabSales Invoice` so on so.name=soi.parent and so.posting_date < DATE_ADD(CURDATE(), INTERVAL -24 MONTH) 
			where item_code=%(item_code)s """, {"item_code":row["item_code"]})
			update_row["above_twenty_four_month_qty"] = above_twenty_four_month_quantity[0]

			data.append(update_row)

	return data


def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("item"):
		conditions += " and soi.item_code = '{0}'".format(filters.get('item'))
	if filters.get("company"):
		conditions += " and soi.company = '{0}'".format(filters.get('company'))	
	if filters.get("warehouse"):
		conditions += " and soi.warehouse = '{0}'".format(filters.get('warehouse'))
	if filters.get("from_date"):
		conditions += " and so.posting_date >= '{0}'".format(filters.get('from_date'))
	if filters.get("to_date"):
		conditions += " and so.posting_date <= '{0}'".format(filters.get('to_date'))
	return conditions



def get_columns():
	return	[
		{
			"label": "Branch",
			"fieldname": "company",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "WareHouse Name",
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Book Code",
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Book Description",
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Available Stock",
			"fieldname": "available_stock",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Last Stock Updated Date",
			"fieldname": "last_stock_updated_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Last Issued Date",
			"fieldname": "last_issued_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Last Received Date",
			"fieldname": "last_received_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "6 Month Quantity",
			"fieldname": "six_month_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "12 Month Quantity",
			"fieldname": "twelve_month_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "18 Month Quantity",
			"fieldname": "eighteen_month_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "24 Month Quantity",
			"fieldname": "twenty_four_month_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Above 24 Month Quantity",
			"fieldname": "above_twenty_four_month_qty",
			"fieldtype": "Data",
			"width": 120
		},		
]