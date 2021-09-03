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
	query_data = frappe.db.sql(""" SELECT a.name, "Payment Entry" as payment_entry, a.posting_date, a.paid_from, a.paid_amount, b.reference_name, b.total_amount, a.payment_type, a.reference_no, a.reference_date, a.total_allocated_amount, a.party_name, a.bank, a.remarks from `tabPayment Entry` a left join `tabPayment Entry Reference` b on a.name=b.parent where a.docstatus=1 and {0}""".format(get_filters_codition(filters)),as_list=True)
	for row in query_data:
		if row[7] == "Receive":
			row.insert(5, "Cr")
		else:
			row.insert(5, "Dr")
		row.insert(13, "")

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
			"label": _("Voucher Number"),
			"fieldname": "voucher_number",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Voucher Type"),
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Voucher Date"),
			"fieldname": "voucher_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Ledger Name"),
			"fieldname": "ledger_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("DR/CR"),
			"fieldname": "dr_cr",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Reference No"),
			"fieldname": "reference_no",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Reference Amount"),
			"fieldname": "reference_amount",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Transaction Type"),
			"fieldname": "transaction_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Inst No"),
			"fieldname": "inst_no",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Inst Date"),
			"fieldname": "inst_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Chq Amount"),
			"fieldname": "chq_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Favoring Name"),
			"fieldname": "favoring_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Bank Name"),
			"fieldname": "bank_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Branch Name"),
			"fieldname": "branch_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Narration"),
			"fieldname": "narration",
			"fieldtype": "Data",
			"width": 120
		}
	]