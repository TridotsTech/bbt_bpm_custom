from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils import add_to_date, date_diff, getdate, nowdate, get_last_day, formatdate, get_link_to_form
from erpnext.accounts.report.general_ledger.general_ledger import execute
from frappe.core.page.dashboard.dashboard import cache_source
from frappe.utils.dateutils import get_from_date_from_timespan, get_period_ending

from frappe.utils.nestedset import get_descendants_of




@frappe.whitelist()
@cache_source
def get_data(chart_name = None, chart = None, no_cache = None, from_date = None, to_date = None):
	print(chart_name,'-----chart_name')
	if chart_name:
		chart = frappe.get_doc('Dashboard Chart', chart_name)
		print(chart,'chart--------')
	else:
		chart = frappe._dict(frappe.parse_json(chart))
	timespan = chart.timespan

	print(timespan,'timespan--------')

	if chart.timespan == 'Select Date Range':
		from_date = chart.from_date
		to_date = chart.to_date

	timegrain = chart.time_interval
	filters = frappe.parse_json(chart.filters_json)
	print(filters,'filters---------------')

	status = filters.get("status")
	print(status,'status------')
	# company = filters.get("company")
	# print(company,'----company')

	if not chart_name:
		frappe.throw(_("Account is not set for the dashboard chart {0}")
			.format(get_link_to_form("Dashboard Chart", chart_name)))

	# if not frappe.db.exists("Account", account) and chart_name:
	# 	frappe.throw(_("Account {0} does not exists in the dashboard chart {1}")
	# 		.format(account, get_link_to_form("Dashboard Chart", chart_name)))

	if not to_date:
		to_date = nowdate()
	if not from_date:
		if timegrain in ('Monthly', 'Quarterly'):
			from_date = get_from_date_from_timespan(to_date, timespan)

	# fetch dates to plot
	dates = get_dates_from_timegrain(from_date, to_date, timegrain)
	print(dates,'dates-----')
	# get all the entries for this account and its descendants
	gl_entries = get_gl_entries()

	print(gl_entries,'gl_entries-------')

	# compile balance values
	result = build_result(dates, gl_entries)

	print(result,'-----result')

	return {
		"labels": [formatdate(r[0].strftime('%Y-%m-%d')) for r in result],
		"datasets": [{
			"name": status,
			"values": [r[1] for r in result]
		}]
	}


def build_result(dates, gl_entries):
	result = [[getdate(date), 0.0] for date in dates]
	# print(result,'result in method')
	# root_type = frappe.db.get_value('Account', account, 'root_type')

	# print(root_type)

	# # start with the first date
	date_index = 0

	# # get balances in debit
	for entry in gl_entries:

	# 	# entry date is after the current pointer, so move the pointer forward
		while getdate(entry.transaction_date) > result[date_index][0]:
			date_index += 1
			print(date_index,'date_index--------')

		# result[date_index][1] += entry.debit - entry.credit

	# if account type is credit, switch balances
	# if root_type not in ('Asset', 'Expense'):
	# 	for r in result:
	# 		r[1] = -1 * r[1]

	# for balance sheet accounts, the totals are cumulative
	# if root_type in ('Asset', 'Liability', 'Equity'):
	for i, r in enumerate(result):
		if i > 0:
			r[1] = r[1] + result[i-1][1]

	return result

def get_gl_entries():
	# child_accounts = get_descendants_of('Account', account, ignore_permissions=True)
	# child_accounts.append(account)

	# return frappe.db.get_all('GL Entry',
	# 	fields = ['posting_date', 'debit', 'credit'],
	# 	filters = [
	# 		dict(posting_date = ('<', to_date)),
	# 		dict(account = ('in', child_accounts)),
	# 		dict(voucher_type = ('!=', 'Period Closing Voucher'))
	# 	],
	# 	order_by = 'posting_date asc')

	return frappe.db.get_all('Sales Order',
		fields = ['status', 'name','transaction_date'],
		filters = [dict(status = ('=', "Draft")),
			])

def get_dates_from_timegrain(from_date, to_date, timegrain):
	days = months = years = 0
	if "Daily" == timegrain:
		days = 1
	elif "Weekly" == timegrain:
		days = 7
	elif "Monthly" == timegrain:
		months = 1
	elif "Quarterly" == timegrain:
		months = 3

	dates = [get_period_ending(from_date, timegrain)]
	while getdate(dates[-1]) < getdate(to_date):
		date = get_period_ending(add_to_date(dates[-1], years=years, months=months, days=days), timegrain)
		dates.append(date)
	return dates