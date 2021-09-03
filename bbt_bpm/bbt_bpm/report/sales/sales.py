from __future__ import unicode_literals
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
	query_data = frappe.db.sql(""" SELECT a.name as voucher_number, "Sales Invoice" as voucher_type, a.posting_date, b.sales_order, a.customer, a.billing_address_gstin, a.address_display, b.income_account, b.item_code, b.warehouse, b.batch_no, b.qty, b.rate, b.amount, a.grand_total, a.customer_address, c.due_date, a.remarks from `tabSales Invoice` a left join `tabSales Invoice Item` b on a.name=b.parent left join `tabPayment Schedule` c on a.name=c.parent where a.docstatus=1 and {0}""".format(get_filters_codition(filters)),as_dict=True)

	for row in query_data:
		registration_type = frappe.db.get_value("Customer", {"name":row.get("customer")}, "gst_category")
		row["registration_type"] = registration_type
		address = frappe.db.get_values("Address", {"name":row.get("customer_address")}, ["country", "state", "pincode"], as_dict=1)
		if address:
			add = {"country":address[0].get("country"), "state":address[0].get("state"), "pincode":address[0].get("pincode")}
			row.update(add)
		taxes_and_charges = frappe.db.sql("""SELECT account_head, rate From `tabSales Taxes and Charges` where parent='{0}' """.format(row.get("voucher_number")), as_dict=True)

		for tax in taxes_and_charges:
			t = tax.get("account_head").split("-")
			if "SGST"==t[0].strip():
				row["sgst_led_name"] = tax.get("account_head")
				sgst=flt(tax.get("rate"))*flt(row.get("amount"))
				row["sgst"]=sgst
			elif "CGST" == t[0].strip():
				row["cgst_led_name"] = tax.get("account_head")
				cgst=flt(tax.get("rate"))*flt(row.get("amount"))
				row["cgst"]=cgst
			elif "IGST" == t[0].strip():
				row["igst_led_name"] = tax.get("account_head")
				igst=flt(tax.get("rate"))*flt(row.get("amount"))
				row["cgst"]=cgst
			else:
				row["additional_ledger"] = tax.get("account_head")
				additional_amt=flt(tax.get("rate"))*flt(row.get("amount"))
				row["additional_amt"]=additional_amt

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
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Order No"),
			"fieldname": "sales_order",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Party Name"),
			"fieldname": "customer",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Registration Type"),
			"fieldname": "registration_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("GSTIN No"),
			"fieldname": "billing_address_gstin",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Country"),
			"fieldname": "country",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("State"),
			"fieldname": "state",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Pincode"),
			"fieldname": "pincode",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Address"),
			"fieldname": "address_display",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Sales Ledger"),
			"fieldname": "income_account",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Due on"),
			"fieldname": "due_date",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Godown"),
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Batch"),
			"fieldname": "batch_no",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Amt"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Additional Ledger"),
			"fieldname": "additional_ledger",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Amount"),
			"fieldname": "additional_amt",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("CGST Led Name"),
			"fieldname": "cgst_led_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("CGST"),
			"fieldname": "cgst",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("SGST Led Name"),
			"fieldname": "sgst_led_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("SGST"),
			"fieldname": "sgst",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("IGST Led Name"),
			"fieldname": "igst_led_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("IGST"),
			"fieldname": "igst",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Total"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Narration"),
			"fieldname": "remarks",
			"fieldtype": "Data",
			"width": 120
		}
	]
