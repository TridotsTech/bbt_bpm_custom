from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from datetime import timedelta,date
import datetime
import calendar
import json
import time
from frappe import _
import requests
import json
from frappe.utils import cint, flt, get_datetime, datetime, date_diff, today, nowdate, getdate
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime

@frappe.whitelist()
def get_items_data():
	items_data = frappe.db.sql("""SELECT name, item_group, description, no_of_items_can_be_packed, carton from `tabItem`""", as_dict=1)

	for row in items_data:
		item_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("name")), as_dict=1)
		carton_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}'""".format(row.get("carton")), as_dict=1)
		item_rate = frappe.db.get_value("Item Price", {"item_code":row.get("name")}, "price_list_rate")
		row["rate"] = item_rate
		row["stock_in_qty"] = item_qty[0].get("actual_qty") if item_qty[0] else 0
		row["carton_qty"] = carton_qty[0].get("actual_qty") if carton_qty[0] else 0

	path = 'bbt_bpm/bbt_bpm/page/customer_portal/customer_portal.html'
	html=frappe.render_template(path,{'data':items_data})
	return {'html':html}