# Copyright (c) 2013, Ashish and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns() 
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data = frappe.db.sql(''' SELECT parent as customer ,item_code as book_code,required_qty as required_qty,required_date as required_date,estimated_date_of_grn as estimated_date_of_grn FROM `tabItem List` WHERE parent = '{}' '''.format(filters.get('customer')),as_dict=True)

	for idx,row in enumerate(data):
		if idx !=0:
			row.update({"customer":" "})

	return data
	


def get_columns():
	return [
		{
			"label": "Customer Name",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options":"Customer",
			"width": 150
		},
		{
			"label": "Book Code/ Name",
			"fieldname": "book_code",
			"fieldtype": "Link",
			"options":"Item",
			"width": 150
		},
		{
			"label": "Required Qty",
			"fieldname": "required_qty",
			"fieldtype": "Int",
			"width": 120
		},

		{
			"label": "Required Date",
			"fieldname": "required_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Estimated date of GRN",
			"fieldname": "estimated_date_of_grn",
			"fieldtype": "Date",
			"width": 120
		}
	]
