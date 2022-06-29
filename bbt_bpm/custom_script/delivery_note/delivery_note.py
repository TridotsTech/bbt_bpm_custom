from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math
from frappe import _, msgprint, scrub
from frappe.utils import has_common
from datetime import date


def on_submit(doc, method):
	for row in doc.items:
		total_allocated_qty = frappe.db.get_value("Item", {"name":row.item_code}, "allocated_qty")			
		allocated_qty = flt(total_allocated_qty)-flt(row.qty)
		frappe.db.set_value("Item", row.item_code, "allocated_qty", allocated_qty)

		total_picked_qty = frappe.db.get_value("Item", {"name":row.item_code}, "picked_qty")
		picked_qty = flt(total_picked_qty)-flt(row.qty)
		frappe.db.set_value("Item", row.item_code, "picked_qty", picked_qty)

		item_qty = frappe.db.get_value("Item", {"name":row.item_code}, "goods_in_transit")
		goods_in_transit = flt(item_qty)+flt(row.qty)
		frappe.db.set_value("Item", row.item_code, "goods_in_transit", goods_in_transit)


def on_update_after_submit(doc, method):
	if doc.delivered:
		for row in doc.items:
			item_qty = frappe.db.get_value("Item", {"name":row.item_code}, "goods_in_transit")	
			goods_in_transit = flt(item_qty)-flt(row.qty)
			frappe.db.set_value("Item", row.item_code, "goods_in_transit", goods_in_transit)


def save(doc, method):
	set_items(doc)

def carton_num(doc):
	indx=0
	count=0
	for i in doc.items:
		# nos_rows += 1
		is_packaging=frappe.db.get_value("Item",i.item_code,"item_group")
		
		if is_packaging in ["Carton","packaging material"]:
			
			start_indx=""
			end_indx=""
			
			# i.carton_no=str(start_indx)+"-"+str(end_indx)
			i.carton_qty = str(start_indx)+"-"+str(end_indx)
			i.no_of_items_can_be_packed = str(start_indx)+"-"+str(end_indx)
		else:
			if not i.carton_qty:
				carton_qty = 0
			else:
				carton_qty =  i.qty

		# carton_no calculation
		if int(i.carton_qty) > 0 and not doc.edit_carton_qty_and_no:
			start_indx=int(indx+1)
			end_indx = count + int(i.carton_qty)
			i.carton_no=str(start_indx)+"-"+str(end_indx)
			indx=end_indx
			count = int(indx)


def set_items(doc):
	
	for item in doc.items:
		is_packaging_item = frappe.db.get_value("Item", item.item_code, "no_of_items_can_be_packed")
		is_carton_req = frappe.db.get_value("Item", item.item_code, "carton")
		item_weight = frappe.db.get_value("Item", item.item_code, "weight_per_unit")
		available_qty = frappe.db.sql_list("""select sum(actual_qty) from tabBin 
							where item_code='{0}' and warehouse='{1}'""".format(item.item_code, item.warehouse))
		item_code = frappe.db.get_value("Item", item.item_code, "item_code")

		if is_packaging_item and not doc.edit_carton_qty_and_no:
			carton_item_doc_name = frappe.get_cached_doc("Item", {"item_code": item_code})
			item.carton_name = carton_item_doc_name.item_code
			qty = item.qty / is_packaging_item
			item.carton_qty = math.ceil(qty)
			item.no_of_items_can_be_packed = is_packaging_item
			item.per_carton_weight_in_kg = carton_item_doc_name.per_carton_weight_kgs
			item.total_carton_weight_in_kg = item_weight * item.qty + item.per_carton_weight_in_kg * item.carton_qty
			item.dimension = carton_item_doc_name.dimension
			item.available_stock = available_qty[0]
			item.used_qty = item.qty
			item.is_free_item = 1

		elif doc.edit_carton_qty_and_no:
			carton_item_doc_name = frappe.get_cached_doc("Item", {"item_code": item_code})
			item.carton_name = carton_item_doc_name.item_code
			item.no_of_items_can_be_packed = is_packaging_item
			item.per_carton_weight_in_kg = carton_item_doc_name.per_carton_weight_kgs
			item.total_carton_weight_in_kg = item_weight * item.qty + item.per_carton_weight_in_kg * item.carton_qty
			item.dimension = carton_item_doc_name.dimension
			item.available_stock = available_qty[0]
			item.used_qty = item.qty
			item.is_free_item = 1


		elif not is_packaging_item:
			item_link = "<a target=_blank href='#Form/Item/{0}'>{1}</a>".format(item.item_code, item.item_code)
			msg = "Kindly Update No. of Item can be packed Field for Item {0}".format(item_link)
			frappe.throw(msg)
	carton_num(doc)



#------------------------------------------------------------------
#Permission Query
#------------------------------------------------------------------
def dn_get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	cust = frappe.db.get_value("Customer", {"user":user}, "name")
	delivery_note=frappe.db.sql("""select name from `tabDelivery Note` where customer='{0}' """.format(cust), as_dict=1)
	dn_list = [ '"%s"'%dn.get("name") for dn in delivery_note ]
	
	roles = frappe.get_roles();
	if user != "Administrator" and has_common(['Customer'],roles) :
		if dn_list:
			return """(`tabDelivery Note`.name in ({0}) )""".format(','.join(dn_list))
		else:
			# return "1=2"
			return """(`tabDelivery Note`.name is null)"""