from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math
from frappe import _, msgprint, scrub
from frappe.utils import has_common
from datetime import date


def on_submit(doc, method=None):
	sales_order = []
	for row in doc.items:
		sales_order.append(row.sales_order)

		sales_qty = frappe.db.sql("""SELECT sum(qty) from  `tabSales Invoice Item` where date_add(curdate(),interval -DAY(curdate())+1 DAY)
		and item_code = '{0}' and docstatus=1 """.format(row.item_code))
		slow_movement_qty = frappe.db.get_value("Item", {"name":row.item_code}, "slow_movement_qty")
		medium_movement_qty = frappe.db.get_value("Item", {"name":row.item_code}, "medium_movement_qty")
		fast_movement_qty = frappe.db.get_value("Item", {"name":row.item_code}, "fast_movement_qty")
		if sales_qty[0][0] <= slow_movement_qty:
			frappe.db.set_value("Item", row.item_code, "movement", 'Slow')
		if (sales_qty[0][0] > slow_movement_qty) and (sales_qty[0][0] <= medium_movement_qty):
			frappe.db.set_value("Item", row.item_code, "movement", 'Medium')
		if (sales_qty[0][0] > medium_movement_qty):
			frappe.db.set_value("Item", row.item_code, "movement", 'Fast')

	if sales_order:
		pick_list = frappe.db.sql("""SELECT distinct parent from `tabPick List Item` where sales_order='{0}' 
									and docstatus=1 """.format(sales_order[0]), as_list=1)

		if pick_list:
			for row in pick_list:
				doc.pick_list_ref = row[0]
				pick_doc = frappe.get_doc("Pick List", row[0])
				pick_doc.append("sales_invoice", {
						"sales_invoice":doc.name,
						"parent":row[0]
					})
				pick_doc.flags.ignore_validate_update_after_submit = True
				pick_doc.save()
				frappe.db.commit()
	

def save(doc, method):
	set_items(doc)

def set_items(doc):
	for item in doc.items:
		is_packaging_item = frappe.db.get_value("Item", item.item_code, "no_of_items_can_be_packed")
		is_carton_req = frappe.db.get_value("Item", item.item_code, "carton")
		available_qty = frappe.db.sql_list("""select sum(actual_qty) from tabBin 
									where item_code='{0}'""".format(item.item_code))
		if is_packaging_item and is_carton_req:
			carton_item_doc = frappe.get_cached_doc("Item", {"item_code": is_carton_req})
			item.available_stock = available_qty[0]
			item.dimension = carton_item_doc.dimension
			item.used_qty = item.qty




#------------------------------------------------------------------
#Permission Query
#------------------------------------------------------------------
def si_get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	cust = frappe.db.get_value("Customer", {"user":user}, "name")

	invoices=frappe.db.sql("""select name from `tabSales Invoice` where customer='{0}' """.format(cust), as_dict=1)

	si_list = [ '"%s"'%si.get("name") for si in invoices ]
	roles = frappe.get_roles();
	if user != "Administrator" and has_common(['Customer'],roles) :
		if si_list:
			return """(`tabSales Invoice`.name in ({0}) )""".format(','.join(si_list))
		else:
			# return "1=2"
			return """(`tabSales Invoice`.name is null)"""