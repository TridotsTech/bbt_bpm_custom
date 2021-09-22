# Copyright (c) 2013, Ashish and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import has_common
import json
from six import StringIO, string_types
from datetime import date
from frappe.utils import cstr, getdate, split_emails, add_days, today, get_last_day, get_first_day, month_diff, nowdate, cint, flt

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data
	
def get_data(filters):
	query_data = frappe.db.sql(""" SELECT  pr.name as voucher_no, "Purchase Receipt" as voucher_type, pr.supplier, 
	pri.purchase_order as ref, pr.posting_date as posting_date, pr.address_display, pr.supplier_gstin as gstin, pri.item_code,
	pri.warehouse, pri.batch_no, pri.qty, c.due_date, pr.remarks
	from `tabPurchase Receipt` pr left JOIN `tabPurchase Receipt Item` pri on
	pr.name=pri.parent left JOIN `tabPayment Schedule` c on pr.name=c.parent and pri.idx=1 and {0}""".format(get_filters_codition(filters)),as_dict=True)
	

	for row in query_data:
		registration_type = frappe.db.get_value("Supplier", {"name":row.get("supplier")}, "gst_category")
		row["registration_type"] = registration_type
		address = frappe.db.get_values("Address", {"name":row.get("supplier_address")}, ["country", "state", "pincode"], as_dict=1)
		if address:
			add = {"country":address[0].get("country"), "state":address[0].get("state"), "pincode":address[0].get("pincode")}
			row.update(add)

		taxes_and_charges = frappe.db.sql_list(""" SELECT account_head From `tabPurchase Taxes and Charges` where parent='{0}'""".format(row['voucher_no']))
		
		if not taxes_and_charges:
			row["account_head"] = "-"
		else:	
			a = ""
			for i in taxes_and_charges:
				a +=  i + ", "
			row["account_head"] = a
		row["tracking_no"] = "-"

	return query_data

def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("voucher_number"):
		conditions += " and pr.name = '{0}'".format(filters.get('voucher_number'))
	if filters.get("from_date"):
		conditions += " and pr.posting_date >= '{0}'".format(filters.get('from_date'))
	if filters.get("to_date"):
		conditions += " and pr.posting_date <= '{0}'".format(filters.get('to_date'))
	return conditions


def get_columns():
	return	[
		{
			"label": "Voucher Number",
			"fieldname": "voucher_no",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Voucher Type",
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Reference Number",
			"fieldname": "ref",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Order Num"),
			"fieldname": "ref",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Order Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("Party Name"),
			"fieldname": "supplier",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Registration Type"),
			"fieldname": "registration_type",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("GSTIN No."),
			"fieldname": "gstin",
			"fieldtype": "Data",
			"width": 150
		},
		# {
		# 	"label": _("Country"),
		# 	"fieldname": "country",
		# 	"fieldtype": "Data",
		# 	"width": 120	
		# },
		# {
		# 	"label": _("State"),
		# 	"fieldname": "state",
		# 	"fieldtype": "Data",
		# 	"width": 120
		# },
		# {
		# 	"label": _("Pincode"),
		# 	"fieldname": "pincode",
		# 	"fieldtype": "Data",
		# 	"width": 120
		# },
		{
			"label": _("Address"),
			"fieldname": "address_display",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Purchase Ledger"),
			"fieldname": "account_head",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Item name"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Tracking No"),
			"fieldname": "tracking_no",
			"fieldtype": "Data",
			"width": 150
		},
		# {
		# 	"label": _("Order No"),
		# 	"fieldname": "order_no",
		# 	"fieldtype": "Data",
		# 	"width": 150
		# },
		{
			"label": _("Order Due Date"),
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Batch"),
			"fieldname": "batch_no",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Narration"),
			"fieldname": "remarks",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("TALLYIMPORTSTATUS"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 150
		}
	]

