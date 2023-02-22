# Copyright (c) 2013, Ashish and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):	
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data

def get_data(filters=None):
	data = frappe.db.sql(""" SELECT name,customer,set_warehouse as service_warehouse from `tabSales Order` """,as_dict=True)

	for row in data:
		delivered_note = frappe.db.sql(""" SELECT DISTINCT parent,against_sales_order from `tabDelivery Note Item` where against_sales_order = '{}' """.format(row.name),as_dict=True)
		pick_list = frappe.db.sql(""" SELECT DISTINCT parent,sales_order FROM `tabPick List Item` where sales_order = '{}' """.format(row.name),as_dict=True)
		
		for pl_name in pick_list:
			if row.name == pl_name.get('sales_order'):
				row.update({"pick_list_number":pl_name.get('parent')})
		for dln_name in delivered_note:
			if row.name == dln_name.get('against_sales_order'):
				row.update({"delivered_note_number":dln_name.get('parent')})

		customer_details = frappe.db.get_value("Customer",{"name":row.get('customer')},['customer_code','customer_name'],as_dict=True)

		row.update({'customer_code':customer_details.customer_code,'customer_name':customer_details.customer_name})
	return data


def get_columns():
	columns = [
		{
			"label": ("Sales Order Number"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options":"Sales Order",
			"width": 160,
		},
		{
			"label": ("Customer Code"),
			"fieldname": "customer_code",
			"fieldtype": "Data",
			"width": 60,
		},
		{
			"label": ("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 260,
		},
		{
			"label": ("Service Warehouse"),
			"fieldname": "service_warehouse",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": ("Pick List Number"),
			"fieldname": "pick_list_number",
			"fieldtype": "Link",
			"options":"Pick List",
			"width": 160,
		},
		{
			"label": ("Delivery Note Number"),
			"fieldname": "delivered_note_number",
			"fieldtype": "Link",
			"options":"Delivery Note",
			"width": 160,
		},
		
	]

	return columns
