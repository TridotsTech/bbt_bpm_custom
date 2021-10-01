from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math

def save(doc, method):
	set_items(doc)

def carton_details(doc):

	indx=0
	for i in doc.locations:
		is_packaging=frappe.db.get_value("Item",i.item_code,"item_group")
		if is_packaging in ["Carton","packaging material"]:
			
			start_indx=""
			end_indx=""
			# indx=end_indx

			i.carton_no=str(start_indx)+"-"+str(end_indx)
			i.carton_qty = str(start_indx)+"-"+str(end_indx)
			i.no_of_items_can_be_packed = str(start_indx)+"-"+ str(end_indx)

		else:
			start_indx=indx+1
			end_indx=start_indx+i.carton_qty-1
			i.carton_no=str(start_indx)+"-"+str(end_indx)
			indx=end_indx

def set_items(doc):
	
	for item in doc.locations:
		is_packaging_item = frappe.db.get_value("Item", item.item_code, "no_of_items_can_be_packed")
		is_carton_req = frappe.db.get_value("Item", item.item_code, "carton")
		
		if is_packaging_item and is_carton_req:
			carton_item_doc_name = frappe.get_cached_doc("Item", {"item_code": is_carton_req})
			qty = item.qty / is_packaging_item
			item.carton_qty = math.ceil(qty)
			item.no_of_items_can_be_packed = is_packaging_item
		elif not is_packaging_item:
			item_link = "<a target=_blank href='#Form/Item/{0}'>{1}</a>".format(item.item_code, item.item_code)
			msg = "Kindly Update No. of Item can be packed Field for Item {0}".format(item_link)
			frappe.throw(msg)
	carton_details(doc)


def on_submit(doc, method=None):
	sales_order = []

	for row in doc.locations:
		sales_order.append(row.sales_order)
		picked_qty = frappe.db.sql("""select sum(picked_qty) from `tabPick List Item` where item_code=%(item_code)s 
		""", {"item_code": row.item_code})

		delivered_qty = frappe.db.sql("""select sum(qty) from `tabDelivery Note Item` soi join `tabWarehouse` w on soi.warehouse=w.name 
            where soi.item_code=%(item_code)s and soi.docstatus=1 and w.is_reserved=1""", {"item_code": row.item_code})
		actual_picked_qty = picked_qty[0][0] - delivered_qty[0][0]
		frappe.db.set_value("Item", row.item_code, "picked_qty", actual_picked_qty)
		

	if sales_order:
		invoices = frappe.db.sql("""SELECT distinct parent from `tabSales Invoice Item` where sales_order='{0}' and docstatus=1 """.format(sales_order[0]), as_list=1)

		invoices_list = []
		for row in doc.sales_invoice:
			invoices_list.append(row.sales_invoice)

		for row in invoices:
			frappe.db.set_value("Sales Invoice", row[0], "pick_list_ref", doc.name)
			if row[0] not in invoices_list:
				doc.append("sales_invoice", {
					"sales_invoice": row[0]
				})
			

def before_save(doc, method=None):
	so_doc = frappe.get_cached_doc("Sales Order", doc.locations[0].sales_order)
	items = []
	for item in so_doc.items:
		
		item_details = frappe.new_doc("Pick List Item")
		item_details.item_code = item.item_code
		item_details.item_name = item.item_name
		item_details.description = item.description
		item_details.item_group =frappe.db.get_value("Item", item.item_code, "item_group")
		item_details.warehouse = item.warehouse
		item_details.qty = item.qty
		item_details.uom = item.uom
		item_details.picked_qty = item.qty
		item_details.stock_uom = item.stock_uom
		item_details.stock_qty = item.stock_qty
		item_details.conversion_factor = item.conversion_factor
		item_details.sales_order = item.parent
		item_details.parent = doc.name
		item_details.parenttype = "Pick List"
		item_details.parentfield = "locations"
		item_details.sales_order_item = item.name
		item_details.idx = item.idx
		items.append(item_details)
	doc.locations = items
	set_items(doc)




