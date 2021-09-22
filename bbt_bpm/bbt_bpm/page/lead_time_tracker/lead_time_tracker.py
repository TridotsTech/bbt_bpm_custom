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
def get_po_details(filters):
	filters=json.loads(filters)
	data = []
	po_name = []
	po_details = frappe.db.sql("""SELECT a.name, a.supplier, a.transaction_date, a.currency, b.item_code, b.description, b.warehouse, b.qty, b.rate, b.billed_amt From `tabPurchase Order` a left join `tabPurchase Order Item` b on a.name=b.parent where {0}""".format(get_filters_codition(filters)), as_dict=1)
	if filters:
		for row in po_details:
			pi_details = frappe.db.sql("""SELECT a.name, a.posting_date, b.qty From `tabPurchase Invoice` a left join `tabPurchase Invoice Item` b on a.name=b.parent where b.purchase_order='{0}' and b.item_code='{1}' """.format(row.get("name"), row.get("item_code")), as_dict=1)
			lead_time= frappe.db.get_all("Purchase Order Item", {"item_code":row.get("item_code")}, "name")
			number_of_shipment = frappe.db.get_all("Purchase Invoice Item", {"item_code":row.get("item_code")}, "name")
			actual_qty = frappe.db.sql("""SELECT sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}' and warehouse='{1}'""".format(row.get("item_code"), row.get("warehouse")), as_dict=1)

			if pi_details:
				actual_lead_time = date_diff(pi_details[0].get("posting_date"), po_details[0].get("transaction_date"))
				row["purchase_inv"] = pi_details[0].get("name")
				row["purchase_inv_date"] = pi_details[0].get("posting_date")
				row["accepted_qty"] = pi_details[0].get("qty")
				row["lead_time"] = len(lead_time)
				row["actual_lead_time"] = str(actual_lead_time)
				row["balance"] = actual_qty[0].get("actual_qty")
				row["number_of_shipment"] = len(number_of_shipment)
			
		path = 'bbt_bpm/bbt_bpm/page/lead_time_tracker/lead_time_tracker.html'
		html=frappe.render_template(path,{'data':po_details})
		return {'html':html}

def get_filters_codition(filters):
	conditions = "1=1"
	if filters.get("purchase_order"):
		conditions += " and a.name = '{0}'".format(filters.get('purchase_order'))
	if filters.get("printer_name"):
		conditions += " and a..supplier = '{0}'".format(filters.get('printer_name'))
	if filters.get("start_date"):
		conditions += " and a.transaction_date >= '{0}'".format(filters.get('start_date'))
	if filters.get("to_date"):
		conditions += " and a.transaction_date <= '{0}'".format(filters.get('to_date'))
	return conditions

@frappe.whitelist()
def custome_report_to_pdf(html, orientation="Landscape"):
	frappe.local.response.filename = "report.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": orientation,'page-size':'A4'})
	frappe.local.response.type = "download"