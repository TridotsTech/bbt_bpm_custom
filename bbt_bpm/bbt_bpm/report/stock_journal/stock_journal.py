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
	query_data = frappe.db.sql(""" SELECT voucher_type, posting_date, voucher_no, item_code, warehouse, qty_after_transaction, _comments,
	valuation_rate, stock_value 
	from `tabStock Ledger Entry` where voucher_type in ('Stock Reconciliation', 'Stock Transfer', 'Material Transfer', 'Material Issue') and docstatus=1 and {0}""".format(get_filters_codition(filters)),as_dict=True)
	
	for itm in query_data:

		dst_warehouse = frappe.db.sql("""SELECT name from `tabWarehouse` where main_warehouse='{0}'""".format(itm.warehouse))
		print(dst_warehouse)
		if dst_warehouse:
			itm["dst_warehouse"] = dst_warehouse[0]
		else:
			itm["dst_warehouse"] = None
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
			"label": "Voucher Type",
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("Voucher Number"),
			"fieldname": "voucher_no",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Source(Consumption)"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Quantity"),
			"fieldname": "qty_after_transaction",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Rate"),
			"fieldname": "valuation_rate",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Amount"),
			"fieldname": "stock_value",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Destination(Production)"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("DST_Warehouse"),
			"fieldname": "dst_warehouse",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("DST_Qty"),
			"fieldname": "qty_after_transaction",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("DST_Rate"),
			"fieldname": "valuation_rate",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("DST_Amount"),
			"fieldname": "stock_value",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Narration"),
			"fieldname": "_comments",
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

