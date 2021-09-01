# Copyright (c) 2013, Bakelite and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import has_common
import json
from six import StringIO, string_types
from datetime import date
from frappe.utils import cstr, getdate, split_emails, add_days, today, get_last_day, get_first_day, month_diff, nowdate, cint, flt, date_diff
from six import iteritems
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import copy

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data
	
def get_data(filters):

	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)
	iwb_map = get_item_warehouse_map(filters, sle)

	item_map = get_item_details(items, sle, filters)
	item_reorder_detail_map = get_item_reorder_details(item_map.keys())
	stock_qty=stock_qty_before_some_month(filters)
	data = []
	conversion_factors = {}

	_func = lambda x: x[1]

	for (company, item, warehouse) in sorted(iwb_map):
		if item_map.get(item):
			qty_dict = iwb_map[(company, item, warehouse)]
			item_reorder_level = 0
			item_reorder_qty = 0
			if item + warehouse in item_reorder_detail_map:
				item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
				item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]
			
			last_stock_updated_date=frappe.db.sql("""SELECT item_code, posting_date from `tabStock Ledger Entry` where item_code='{0}' and company='{1}' and warehouse='{2}' ORDER BY posting_date DESC """.format(item, company, warehouse), as_dict=1)

			if item in stock_qty and stock_qty.get(item).get("warehouse")==warehouse:
				report_data = {
					'currency': company_currency,
					'item_code': item,
					'warehouse': warehouse,
					'company': company,
					'reorder_level': item_reorder_level,
					'reorder_qty': item_reorder_qty,
					'last_stock_updated_date':last_stock_updated_date[0].get("posting_date") if last_stock_updated_date[0] else "",
					'days_60':stock_qty.get(item).get(2, 0),
					'days_90':stock_qty.get(item).get(3, 0),
					'days_180':stock_qty.get(item).get(6, 0),
					'year_1':stock_qty.get(item).get(12, 0),
					'year_2':stock_qty.get(item).get(24, 0)
				}
			else:
				report_data = {
					'currency': company_currency,
					'item_code': item,
					'warehouse': warehouse,
					'company': company,
					'reorder_level': item_reorder_level,
					'reorder_qty': item_reorder_qty,
					'last_stock_updated_date':last_stock_updated_date[0].get("posting_date") if last_stock_updated_date[0] else ""
				}


			report_data.update(item_map[item])
			report_data.update(qty_dict)
			data.append(report_data)


	return data


def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = ' and sle.item_code in ({})'\
			.format(', '.join([frappe.db.escape(i, percent=False) for i in items]))

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
			sle.item_code as name, sle.voucher_no, sle.stock_value, sle.name
		from
			`tabStock Ledger Entry` sle force index (posting_sort_index)
		where sle.docstatus < 2 %s %s
		order by sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty""" % #nosec
		(item_conditions_sql, conditions), as_dict=1)


def get_conditions(filters):
	conditions = ""
	# if not filters.get("from_date"):
	# 	frappe.throw(_("'From Date' is required"))

	# if filters.get("to_date"):
	# 	conditions += " and sle.posting_date <= %s" % frappe.db.escape(filters.get("to_date"))
	# else:
	# 	frappe.throw(_("'To Date' is required"))

	if filters.get("company"):
		conditions += " and sle.company = %s" % frappe.db.escape(filters.get("company"))

	if filters.get("warehouse"):
		warehouse_details = frappe.db.get_value("Warehouse",
			filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
		if warehouse_details:
			conditions += " and exists (select name from `tabWarehouse` wh \
				where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)"%(warehouse_details.lft,
				warehouse_details.rgt)


	# if filters.get("warehouse_type") and not filters.get("warehouse"):
	# 	conditions += " and exists (select name from `tabWarehouse` wh \
	# 		where wh.warehouse_type = '%s' and sle.warehouse = wh.name)"%(filters.get("warehouse_type"))

	return conditions


def get_item_warehouse_map(filters, sle):
	iwb_map = {}
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	for d in sle:
		key = (d.company, d.item_code, d.warehouse)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0
			})

		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]
		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - flt(qty_dict.bal_qty)
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)
		# if d.posting_date < from_date:
		# 	qty_dict.opening_qty += qty_diff
		# 	qty_dict.opening_val += value_diff

		# elif d.posting_date >= from_date and d.posting_date <= to_date:
		# 	if flt(qty_diff, float_precision) >= 0:
		# 		qty_dict.in_qty += qty_diff
		# 		qty_dict.in_val += value_diff
		# 	else:
		# 		qty_dict.out_qty += abs(qty_diff)
		# 		qty_dict.out_val += abs(value_diff)
		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff
	iwb_map = filter_items_with_no_transactions(iwb_map, float_precision)

	return iwb_map


def filter_items_with_no_transactions(iwb_map, float_precision):
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]

		no_transactions = True
		for key, val in iteritems(qty_dict):
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False

		if no_transactions:
			iwb_map.pop((company, item, warehouse))

	return iwb_map

def get_item_details(items, sle, filters):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sle]))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if filters.get("include_uom"):
		cf_field = ", ucd.conversion_factor"
		cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%s" \
			% frappe.db.escape(filters.get("include_uom"))

	res = frappe.db.sql("""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom %s
		from
			`tabItem` item
			%s
		where
			item.name in (%s)
	""" % (cf_field, cf_join, ','.join(['%s'] *len(items))), items, as_dict=1)

	for item in res:
		item_details.setdefault(item.name, item)

	if filters.get('show_variant_attributes', 0) == 1:
		variant_values = get_variant_values_for(list(item_details))
		item_details = {k: v.update(variant_values.get(k, {})) for k, v in iteritems(item_details)}

	return item_details

def get_item_reorder_details(items):
	item_reorder_details = frappe._dict()

	if items:
		item_reorder_details = frappe.db.sql("""
			select parent, warehouse, warehouse_reorder_qty, warehouse_reorder_level
			from `tabItem Reorder`
			where parent in ({0})
		""".format(', '.join([frappe.db.escape(i, percent=False) for i in items])), as_dict=1)

	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)


def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def stock_qty_before_some_month(filters):
	months_list = [2, 3, 6, 12, 24]
	months_date = []
	# months_date.append(getdate(today()))
	for row in months_list:
		_date = date.today() + relativedelta(months=-row)
		months_date.append(getdate(_date))

	new_list = {}
	stock_dict = {}
	for idx, v in enumerate(months_date):
		month_len = len(months_date)-1
		if month_len != idx:
			sle_qty = frappe.db.sql("""select sle.item_code, sle.warehouse, sle.posting_date, ABS(sum(sle.actual_qty) - sum(sle.qty_after_transaction)) as bal_qty, sle.company from `tabStock Ledger Entry` sle where sle.company='{0}' and sle.posting_date BETWEEN '{1}' and '{2}' GROUP BY sle.item_code, sle.warehouse""".format(filters.get("company"), months_date[idx+1], v), as_dict=1)
		else:
			sle_qty = frappe.db.sql("""select distinct sle.item_code, sle.warehouse, sle.posting_date, ABS(sum(sle.actual_qty) - sum(sle.qty_after_transaction)) as bal_qty, sle.company from `tabStock Ledger Entry` sle where sle.company='{0}' and sle.posting_date < '{1}' GROUP BY sle.item_code, sle.warehouse""".format(filters.get("company"), v), as_dict=1)
		
		for row in sle_qty:
			if row.get("item_code") in stock_dict:
				d=stock_dict[row.get("item_code")]
				d[months_list[idx]]=row.get("bal_qty")
				stock_dict[row.get("item_code")]=d
			else:
				row[months_list[idx]]=row.get("bal_qty")
				stock_dict[row.get("item_code")] = row

	return stock_dict

def get_columns():
	return	[
		{
			"label": _("Branch"),
			"fieldname": "company",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
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
			"label": _("Book Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Last Stock Updated Date"),
			"fieldname": "last_stock_updated_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("Available Stock"),
			"fieldname": "bal_qty",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("0-30 Days"),
			"fieldname": "days_30",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("60 Days"),
			"fieldname": "days_60",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("90 Days"),
			"fieldname": "days_90",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("180 Days"),
			"fieldname": "days_180",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("1 Year"),
			"fieldname": "year_1",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _(">2 Year"),
			"fieldname": "year_2",
			"fieldtype": "Data",
			"width": 150
		}
	]