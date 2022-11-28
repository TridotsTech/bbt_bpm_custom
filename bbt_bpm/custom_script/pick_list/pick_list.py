from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math


from frappe.model.mapper import map_child_doc
from erpnext.selling.doctype.sales_order.sales_order import (
	make_delivery_note as create_delivery_note_from_sales_order,
)
from erpnext.stock.doctype.pick_list.pick_list import update_delivery_note_item,set_delivery_note_missing_values,validate_item_locations

def save(doc, method):
	set_so_qty(doc)
	set_items(doc)
	carton_data(doc)


def carton_details(doc):
	for i in doc.get("locations"):
		is_packaging=frappe.db.get_value("Item",i.item_code,"item_group")
		if is_packaging in ["Carton","packaging material"]:
			
			start_indx=""
			end_indx=""
			# indx=end_indx

			#i.carton_qty = str(start_indx)+"-"+str(end_indx)
			i.no_of_items_can_be_packed = str(start_indx)+"-"+ str(end_indx)
		
		else:
			if not i.carton_qty:
				carton_qty = 0
			else:
				# carton_qty = i.carton_qty
				#i.carton_qty =  i.qty
				carton_qty =  i.qty
				#carton_qty = doc.locations[int(i.idx)].qty

	calculate_carton_no(doc)
			
def set_items(doc):
	for item in doc.locations:
		is_packaging_item = frappe.db.get_value("Item", item.item_code, "no_of_items_can_be_packed")
		is_carton_req = frappe.db.get_value("Item", item.item_code, "carton")
		if is_packaging_item:
			# carton_item_doc_name = frappe.get_cached_doc("Item", {"item_code": is_carton_req})

			qty = item.qty / is_packaging_item
			if not doc.edit_carton_qty_and_no:
				item.carton_qty = qty

			# elif doc.edit_carton_qty_and_no:
			# 	item.carton_qty = None

			#print('\n\nIs packaging Item - \n\n',is_packaging_item)
			#print('item index__________	',int(item.idx))
			# item.carton_qty = doc.locations[int(item.idx)+1].qty
			item.no_of_items_can_be_packed = is_packaging_item
				
		elif not is_packaging_item:
			item_link = "<a target=_blank href='/app/Item/{0}'>{1}</a>".format(item.item_code, item.item_code)
			msg = "Kindly Update No. of Item can be packed Field for Item {0}".format(item_link)
			frappe.throw(msg)

	carton_details(doc)

def carton_data(doc):
	total_craton_weight = []
	try:
		for row in doc.locations:
			if not doc.edit_carton_qty_and_no:
				if row.so_qty > 0:
					total_weight = row.carton_qty * row.per_carton_weight_kgs
					row.total_weight = total_weight
					row.total_carton_weight_in_kg = total_weight

				elif row.so_qty == 0:
					row.total_weight = 0
					row.total_carton_weight_in_kg = 0

			elif doc.edit_carton_qty_and_no:
				if row.so_qty > 0:
					total_weight = row.carton_qty * row.per_carton_weight_kgs
					row.total_weight = total_weight
					row.total_carton_weight_in_kg = total_weight

				else:
					row.total_weight = row.total_weight
					row.total_carton_weight_in_kg = row.total_carton_weight_in_kg

			total_craton_weight.append(float(row.total_carton_weight_in_kg))
		doc.total_craton_weight = sum(total_craton_weight)
	except Exception as e:
		print(e)

def calculate_carton_no(doc):
	indx=0
	count=0
	for i in doc.locations:
		if not doc.edit_carton_qty_and_no and int(i.carton_qty) > 0:
			start_indx=int(indx+1)
			end_indx = count + int(i.carton_qty)
			i.carton_no=str(start_indx)+"-"+str(end_indx)
			indx=end_indx
			count = int(indx)

		# elif int(i.carton_qty) == 0:
		# 	i.carton_no = str(input())

		# elif doc.edit_carton_qty_and_no:
		# 	i.carton_no == None


def on_submit(doc, method=None):
	sales_order = []

	for row in doc.locations:
		sales_order.append(row.sales_order)
		picked_qty = frappe.db.sql("""select sum(picked_qty) from `tabPick List Item` where item_code=%(item_code)s""", {"item_code": row.item_code})

		delivered_qty = frappe.db.sql("""select sum(qty) from `tabDelivery Note Item` soi join `tabWarehouse` w on soi.warehouse=w.name 
            where soi.item_code=%(item_code)s and soi.docstatus=1 and w.is_reserved=1""", {"item_code": row.item_code})
		
		if picked_qty[0][0] == None:
			picked_qty_1 = 0
		else:
			picked_qty_1 = picked_qty[0][0]

		if delivered_qty[0][0] == None:
			delivered_qty_1 = 0
		else:
			delivered_qty_1 = delivered_qty[0][0]
		
		actual_picked_qty = picked_qty_1 - delivered_qty_1
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


def sort_table(doc):

	if doc.sort_table_carton_no_wise: # check

		# Sort locations table carton_no wise
		for i, item in enumerate(sorted(doc.locations, key=lambda item:int(item.carton_no) if '-' not in item.carton_no else False), start=1):
			item.idx = i


# Fetch qty in PL from SO, update in custom so_qty field
def set_so_qty(doc):
	l = []
	for i in doc.locations:
		so_number = i.sales_order
		l.append(so_number)

	so_no = l[0]

	so_data = frappe.db.sql("""SELECT DISTINCT soi.item_code,soi.qty FROM `tabSales Order Item` as soi, `tabPick List Item` as pli
						WHERE soi.parent = %(so_no)s ORDER BY soi.idx;""", {"so_no":so_no},as_dict=1)

	print(f'\n\n{so_data}\n\n')
	# print('\n\nfrappe.db.get_value("Item",i.item_code,"no_of_items_can_be_packed")\n\n')

	for i in doc.locations:
		for x in so_data:
			
			# print(f'\n\n{type(i.no_of_items_can_be_packed)}\n\n')
			# print(f'\n\n{type(i.qty)}\n\n')

			if i.qty == x['qty'] and i.item_code == x['item_code']:
				i.so_qty = x['qty']

			# loops = math.floor(int(i.qty)/int(i.no_of_items_can_be_packed))
			# print(loops)
			if int(i.no_of_items_can_be_packed) > 0:
				if i.item_code == x['item_code'] and int(i.qty) % int(i.no_of_items_can_be_packed) == 0:
			 		i.so_qty = x['qty']


def before_save(doc, method=None):
	set_so_qty(doc)
	sort_table(doc)
	# so_doc = frappe.get_cached_doc("Sales Order", doc.locations[0].sales_order)
	# items = []
	# for item in so_doc.items:
		
	# 	item_details = frappe.new_doc("Pick List Item")
	# 	item_details.item_code = item.item_code
	# 	item_details.item_name = item.item_name
	# 	item_details.description = item.description
	# 	item_details.item_group =frappe.db.get_value("Item", item.item_code, "item_group")
	# 	item_details.warehouse = item.warehouse
	# 	item_details.qty = item.qty
	# 	item_details.uom = item.uom
	# 	item_details.picked_qty = item.qty
	# 	item_details.stock_uom = item.stock_uom
	# 	item_details.stock_qty = item.stock_qty
	# 	item_details.conversion_factor = item.conversion_factor
	# 	item_details.sales_order = item.parent
	# 	item_details.parent = doc.name
	# 	item_details.parenttype = "Pick List"
	# 	item_details.parentfield = "locations"
	# 	item_details.sales_order_item = item.name
	# 	item_details.idx = item.idx
	# 	items.append(item_details)
	# doc.locations = items
	# set_items(doc)


@frappe.whitelist()
def create_delivery_notes(source_name, target_doc=None):
	pick_list = frappe.get_doc('Pick List', source_name)
	validate_item_locations(pick_list)

	sales_orders = [d.sales_order for d in pick_list.locations if d.sales_order]
	sales_orders = set(sales_orders)

	delivery_note = None
	for sales_order in sales_orders:
		delivery_note = create_delivery_note_from_sales_order(sales_order,
			delivery_note, skip_item_mapping=True)

	# map rows without sales orders as well
	if not delivery_note:
		delivery_note = frappe.new_doc("Delivery Note")

	item_table_mapper = {
		'doctype': 'Delivery Note Item',
		'field_map': {
			'rate': 'rate',
			'name': 'so_detail',
			'parent': 'against_sales_order',
		},
		'condition': lambda doc: abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier!=1
	}

	item_table_mapper_without_so = {
		'doctype': 'Delivery Note Item',
		'field_map': {
			'rate': 'rate',
			'name': 'name',
			'parent': '',
		}
	}

	for location in pick_list.locations:
		if location.sales_order_item:
			sales_order_item = frappe.get_cached_doc('Sales Order Item', {'name':location.sales_order_item})
		else:
			sales_order_item = None

		source_doc, table_mapper = [sales_order_item, item_table_mapper] if sales_order_item \
			else [location, item_table_mapper_without_so]

		dn_item = map_child_doc(source_doc, delivery_note, table_mapper)

		if dn_item:
			dn_item.warehouse = location.warehouse
			dn_item.qty = location.picked_qty
			dn_item.batch_no = location.batch_no
			dn_item.serial_no = location.serial_no

			update_delivery_note_item(source_doc, dn_item, delivery_note)

	set_delivery_note_missing_values(delivery_note)

	delivery_note.pick_list = pick_list.name
	delivery_note.customer = pick_list.customer if pick_list.customer else None

	return delivery_note
	
	

