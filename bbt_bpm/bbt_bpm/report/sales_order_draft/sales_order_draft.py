# Copyright (c) 2013, Ashish and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json


def execute(filters=None):
	columns = get_columns() 
	data = get_data(filters)
	return columns, data

@frappe.whitelist()	
def get_data(filters=None):
	return frappe.db.sql("""SELECT * from `tabSales Order` """)

def get_columns():
	return	[
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		}
		# {
		# 	"label": "Title",
		# 	"fieldname": "title",
		# 	"fieldtype": "Data",
		# 	"width": 150
		# },
		
	]

