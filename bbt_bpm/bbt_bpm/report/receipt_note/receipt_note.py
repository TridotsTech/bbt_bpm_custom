# Copyright (c) 2013, Ashish and contributors
# For license information, please see license.txt

import frappe
from frappe import _
# from frappe.utils import has_common
# import json
# from six import StringIO, string_types
# from datetime import date
# from frappe.utils import cstr, getdate, split_emails, add_days, today, get_last_day, get_first_day, month_diff, nowdate, cint

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data
	
def get_data(filters):
	query_data = frappe.db.sql(""" SELECT a.name, "Payment Entry" as payment_entry, a.posting_date, a.paid_from, a.paid_amount, b.reference_name, b.total_amount, a.payment_type, a.reference_no, a.reference_date, a.total_allocated_amount, a.party_name, a.bank, a.remarks from `tabPayment Entry` a left join `tabPayment Entry Reference` b on a.name=b.parent where a.docstatus=1 and {0}""".format(get_filters_codition(filters)),as_list=True)
	
	return query_data

def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("voucher_number"):
		conditions += " and a.name = '{0}'".format(filters.get('voucher_number'))
	if filters.get("from_date"):
		conditions += " and a.posting_date >= '{0}'".format(filters.get('from_date'))
	if filters.get("to_date"):
		conditions += " and a.posting_date <= '{0}'".format(filters.get('to_date'))
	return conditions


def get_columns():
	return	[
		{
			"label": "Voucher Number",
			"fieldname": "",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Voucher Type",
			"fieldname": "",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": "Date",
			"fieldname": "",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Reference Number",
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Warehouse"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Quantity"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Rate"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Amount"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Destination(Production)"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Dest Waarehouse"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Dest Qty"),
			"fieldname": "",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Dest Rate"),
			"fieldname": "",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Dest Amount"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Narration"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Tally Import Status"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 150
		}
	]

