# Copyright (c) 2013, Bakelite and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import has_common
import json
from six import StringIO, string_types
from datetime import date
from frappe.utils import cstr, getdate, split_emails, add_days, today, get_last_day, get_first_day, month_diff, nowdate, cint

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data
	
def get_data(filters):
	query_data = frappe.db.sql(""" SELECT a.name, a.company, a.customer, b.warehouse, a.order_type, a.transaction_date, a.order_class, a.po_no as referce_no, b.item_code, b.qty, "0" as cancelled_qty, b.qty as net_ordered_quantity, "0" as invoiced_qty,  "0" as pending_qty, "0" as allocated_qty, "0" as pick_qty, "BO_aty" as bo_qty, "0" as available_stock, a.docstatus from `tabSales Order` a left join `tabSales Order Item` b on a.name=b.parent where a.docstatus=1 and {0}""".format(get_filters_codition(filters)),as_dict=True)

	cancel_order = frappe.db.sql(""" SELECT a.name, a.company, a.customer, b.warehouse, a.order_type, a.transaction_date, a.order_class, a.po_no as referce_no, b.item_code, b.qty as cancelled_qty, b.qty as net_ordered_quantity, "0" as invoiced_qty,  "0" as pending_qty, "Allocate_qty" as allocated_qty, "0" as pick_qty, "BO_aty" as bo_qty, "0" as available_stock from `tabSales Order` a left join `tabSales Order Item` b on a.name=b.parent where a.docstatus=2 and {0}""".format(get_filters_codition(filters)),as_dict=True)

	# where {0}""".format(get_filters_codition(filters)),as_dict=True, debug=1)
	cancel_order_name = []
	for cancel_ord in cancel_order:
		query_data.append(cancel_ord)

	for row in query_data:
		sales_invoice=frappe.db.sql("""SELECT sum(qty) as qty From `tabSales Invoice Item` where item_code='{0}' and sales_order='{1}' and docstatus=1""".format(row.get("item_code"), row.get("name")), as_dict=1)
		
		pick_qty = frappe.db.sql("""SELECT sum(picked_qty) as picked_qty from `tabPick List Item` where item_code='{0}' and sales_order='{1}' """.format(row.get("item_code"), row.get("name")), as_dict=1)

		if sales_invoice[0].get("qty"):
			row["pick_qty"]=0
			row["invoiced_qty"] = sales_invoice[0].get("qty")
			row["pending_qty"] = row.get("qty")-sales_invoice[0].get("qty")
		else:
			row["pick_qty"]=pick_qty[0].get("picked_qty") if pick_qty[0].get("picked_qty") else 0

		if not sales_invoice[0].get("qty") and not pick_qty[0].get("picked_qty") and row.get("docstatus")==1:
			row["allocated_qty"] = row.get("qty")

		row["bo_qty"] = cint(row.get("net_ordered_quantity")) - (cint(row.get("invoiced_qty"))-cint(row.get("allocated_qty"))-cint(row.get("picked_qty")))

		available_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}' and warehouse='{1}'""".format(row.get("item_code"), row.get("warehouse")), as_dict=1, debug=1)

		row["available_stock"]=available_qty[0].get("actual_qty")

	return query_data

def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("item"):
		conditions += " and b.item_code = '{0}'".format(filters.get('item'))
	if filters.get("warehouse"):
		conditions += " and b.warehouse = '{0}'".format(filters.get('warehouse'))
	if filters.get("from_date"):
		conditions += " and a.transaction_date >= '{0}'".format(filters.get('from_date'))
	if filters.get("to_date"):
		conditions += " and a.transaction_date <= '{0}'".format(filters.get('to_date'))
	return conditions

def get_columns():
	return	[
		{
			"label": _("Branch"),
			"fieldname": "company",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Party Name"),
			"fieldname": "customer",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("WareHouse Name"),
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Order Type"),
			"fieldname": "order_type",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Order Date"),
			"fieldname": "transaction_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Order Class"),
			"fieldname": "order_class",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Books Order #"),
			"fieldname": "referce_no",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Book Code"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Order Quantity"),
			"fieldname": "qty",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Cancelled Quantity"),
			"fieldname": "cancelled_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Net Ordered Quantity"),
			"fieldname": "net_ordered_quantity",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Invoiced Qty"),
			"fieldname": "invoiced_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Pending Quantity"),
			"fieldname": "pending_qty",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Allocated Qty"),
			"fieldname": "allocated_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Picked Qty"),
			"fieldname": "pick_qty",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("BO Qty"),
			"fieldname": "bo_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Available Stock"),
			"fieldname": "available_stock",
			"fieldtype": "Data",
			"width": 120
		}
	]