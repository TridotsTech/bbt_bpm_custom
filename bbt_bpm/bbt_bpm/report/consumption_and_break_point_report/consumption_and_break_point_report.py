# Copyright (c) 2013, Ashish and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data



def get_data(filters):
	query_data = frappe.db.sql("""SELECT DISTINCT
								itm.name, 
								itm.item_code, 
								itm.description
							FROM 
								tabItem itm
							 """,
				as_dict=True)



	for row in query_data:
		available_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}' 
		""".format(row.get("item_code")), as_dict=1)
		row["available_stock"]=available_qty[0].get("actual_qty")
		
		po_details = frappe.db.sql(""" SELECT poi.qty as qty, poi.rate as rate, po.company as company, 
		po.supplier as printer, po.schedule_date as delivery_date
		from `tabPurchase Order` po 
		JOIN `tabPurchase Order Item` poi on po.name=poi.parent and poi.item_code=%(item_code)s and po.docstatus=1 LIMIT 3
		""", {"item_code":row.item_code}, as_dict = 1)
		print(po_details)

		if len(po_details) > 1:
			row["previous_po_qty"] = po_details[1].get("qty")
			row["previous_po_rate"] = po_details[1].get("rate")
			row["previous_printer_name"]=po_details[1].get("printer")
			row["printer"] = po_details[0].get("printer")
			row["current_po_qty"] = po_details[0].get("qty")
			row["current_po_rate"] = po_details[0].get("rate")
			row["company"] = po_details[0].get("company")
			row["delivery_date"] = po_details[0].get("delivery_date")

		else:
			row["previous_po_qty"] = 0
			row["previous_po_rate"] = 0
			row["previous_printer_name"]= None
			row["printer"] = None
			row["current_po_qty"] = 0
			row["current_po_rate"] = 0
			row["company"] = None
			row["delivery_date"] = None
			

		multiple_po_and_dates = frappe.db.sql("""select GROUP_CONCAT( DISTINCT po.name separator " , ") as po_names, 
		GROUP_CONCAT( po.transaction_date separator " , ") as po_dates from  `tabPurchase Order` po JOIN 
		`tabPurchase Order Item` poi on po.name=poi.parent where item_code = %(item_code)s""", {"item_code":row.item_code}, as_dict=1)
		
		row["po_names"] = multiple_po_and_dates[0].get("po_names")
		row["po_dates"] = multiple_po_and_dates[0].get("po_dates")
		
	return query_data



def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("item"):
		conditions += " and poi.item_code = {0}".format(filters.get('item'))
	if filters.get("from_date"):
		conditions += " and po.transaction_date >= '{0}'".format(filters.get('from_date'))
	if filters.get("to_date"):
		conditions += " and po.transaction_date <= '{0}'".format(filters.get('to_date'))
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
			"label": "Re-Order Level",
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Last Sale Date",
			"fieldname": "",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": "Previous Printer Name ",
			"fieldname": "previous_printer_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Previous PO Quantity",
			"fieldname": "previous_po_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Previous PO Price",
			"fieldname": "previous_po_rate",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Current Printer Name",
			"fieldname": "printer",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Current PO Quantity",
			"fieldname": "current_po_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Current PO Price",
			"fieldname": "current_po_rate",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Yet To Recieve From Printer",
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "PO#",
			"fieldname": "po_names",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "PO Date",
			"fieldname": "po_dates",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Expected Delivery Date",
			"fieldname": "delivery_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Remarks",
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Status",
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
	]
