from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr,flt
import json
import math
from frappe import _, msgprint, scrub
from frappe.utils import has_common
from datetime import date

from frappe.utils import get_site_path
import base64



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

	''' Dispatch Order Email Trigger'''

	dict_list = []
	_file_name = frappe.db.sql('''SELECT file_name from `tabFile` where attached_to_name = '{0}' '''.format(doc.name),as_dict=True)
	for file in _file_name:
		private_path = get_site_path("private", "files")
		public_path = get_site_path("public", "files")
		if public_path:
			path = public_path + "/"+ file.get('file_name')
		elif private_path:
			path = private_path + "/"+ file.get('file_name')
		image_file = open(path, "rb")

		encoded_string = ""
		image_file.seek(0)
		encoded_string = image_file.read()
		dict_list.append({"fname":file.get('file_name'),"fcontent":encoded_string})

	print_format = "New Delivery Note" if not cint(frappe.db.get_value('Print Format', 'New Delivery Note', 'disabled')) else None

	default_attachment = frappe.attach_print('Delivery Note', doc.name, print_format=print_format)

	dict_list.append(default_attachment)

	args = {"doc":doc}
	_path = 'bbt_bpm/custom_script/delivery_note/dispatch_order.html'
	# user = frappe.db.get_value("Customer",{"name":doc.customer},"user")
	user = 'swapnilpawar26041999@gmail.com'

	frappe.sendmail(
		user,
		subject= doc.customer+ " " + 'Dispatch Details #: ' + doc.name,
		cc = ["amit.parab@i2econsulting.com","swapnil.pawar@i2econsulting.com",
				"admin@indiabbt.com",
				"frontoffice@indiabbt.com"],
		content=frappe.render_template(_path,args),
		attachments = dict_list,
        
		)

	
def on_update_after_submit(doc, method):
	if doc.delivered:
		for row in doc.items:
			item_qty = frappe.db.get_value("Item", {"name":row.item_code}, "goods_in_transit")	
			goods_in_transit = flt(item_qty)-flt(row.qty)
			frappe.db.set_value("Item", row.item_code, "goods_in_transit", goods_in_transit)

	''' Order Delivery Confirmation  '''

	if doc.delivered and doc.delivery_confirmed:
		dict_list = []
		_file_name = frappe.db.sql('''SELECT file_name from `tabFile` where attached_to_name = '{0}' '''.format(doc.name),as_dict=True)
		for file in _file_name:
			private_path = get_site_path("private", "files")
			public_path = get_site_path("public", "files")
			if public_path:
				path = public_path + "/"+ file.get('file_name')
			elif private_path:
				path = private_path + "/"+ file.get('file_name')
			image_file = open(path, "rb")

			encoded_string = ""
			image_file.seek(0)
			encoded_string = image_file.read()
			dict_list.append({"fname":file.get('file_name'),"fcontent":encoded_string})

		print_format = "New Delivery Note" if not cint(frappe.db.get_value('Print Format', 'New Delivery Note', 'disabled')) else None

		default_attachment = frappe.attach_print('Delivery Note', doc.name, print_format=print_format)
		dict_list.append(default_attachment)
		
		args = {"doc":doc}
		_path = 'bbt_bpm/custom_script/delivery_note/order_delivery_confirmation.html'
		
		# user = frappe.db.get_value("Customer",{"name":doc.customer},"user")
		user = 'swapnilpawar26041999@gmail.com'
		frappe.sendmail(
			user,
			subject = 'Order Delivery Confirmation -'+ " " + doc.customer,
			cc = ["amit.parab@i2econsulting.com","swapnil.pawar@i2econsulting.com",
				"admin@indiabbt.com",
				"frontoffice@indiabbt.com"],
			content=frappe.render_template(_path,args),
			attachments = dict_list,

			)	


def save(doc, method):
	set_items(doc)
	
def carton_num(doc):
	indx=0
	count=0
	for i in doc.items:
		# nos_rows += 1
		is_packaging=frappe.db.get_value("Item",i.item_code,"item_group")
		is_packaging_item = frappe.db.get_value("Item", i.item_code, "no_of_items_can_be_packed")

		
		if is_packaging in ["Carton","packaging material"]:
			
			start_indx=""
			end_indx=""
			
			# i.carton_no=str(start_indx)+"-"+str(end_indx)
			#i.carton_qty = str(start_indx)+"-"+str(end_indx)
			i.no_of_items_can_be_packed = str(start_indx)+"-"+str(end_indx)
		else:
			i.carton_qty = i.carton_qty
			if not i.carton_qty:
				carton_qty = 0
			else:
				carton_qty =  i.qty

		#carton_no calculation
		# if int(i.carton_qty) > 1 and not doc.edit_carton_qty_and_no:
		# 	print('if carton_qty----------------',i.carton_qty)
		# 	start_indx=int(indx+1)
		# 	end_indx = count + int(i.carton_qty)
		# 	i.carton_no=str(start_indx)+"-"+str(end_indx)
		# 	indx=end_indx
		# 	count = int(indx)

		if is_packaging_item and not doc.edit_carton_qty_and_no:
			_carton_no = i.qty / is_packaging_item
			if _carton_no <= 1:
				start_indx=int(indx+1)
				end_indx = count + int(i.carton_qty)
				i.carton_no=str(start_indx)+"-"+str(end_indx)
				indx=end_indx
				count = int(indx)
			else:
				i.carton_no = i.carton_no

		#carton_no calculation
		# if not doc.edit_carton_qty_and_no:
		# 	#i.carton_no=str(start_indx)+"-"+str(end_indx)
		# 	#i.carton_no = frappe.db.get_value("Pick List Item",{"name":i.item_code}, "carton_no")
		# 	i.carton_no = frappe.db.sql(""" SELECT carton_no FROM `tabPick List Item` pli WHERE pli.parent = """, as_dict = 1) 
		# 	print(f'\n\n\n{i.carton_no}\n\n\n')


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
			#print('\n\n Qty \n\n', qty)
			# item.carton_qty = math.floor(qty)
			#print('\n\n Carton Qty \n\n', item.carton_qty)
			item.no_of_items_can_be_packed = is_packaging_item
			item.per_carton_weight_in_kg = carton_item_doc_name.per_carton_weight_kgs
			# item.total_carton_weight_in_kg = item.per_carton_weight_in_kg * item.carton_qty
			item.dimension = carton_item_doc_name.dimension
			item.available_stock = available_qty[0]
			item.used_qty = item.qty
			item.is_free_item = 1

			if qty >= 1:
				item.carton_qty = math.floor(qty)
			else:
				item.carton_qty = item.carton_qty


		elif doc.edit_carton_qty_and_no:
			carton_item_doc_name = frappe.get_cached_doc("Item", {"item_code": item_code})
			item.carton_name = carton_item_doc_name.item_code
			item.no_of_items_can_be_packed = is_packaging_item
			item.per_carton_weight_in_kg = carton_item_doc_name.per_carton_weight_kgs
			# item.total_carton_weight_in_kg = item.per_carton_weight_in_kg * item.carton_qty
			item.dimension = carton_item_doc_name.dimension
			item.available_stock = available_qty[0]
			item.used_qty = item.qty
			item.is_free_item = 1


		elif not is_packaging_item:
			item_link = "<a target=_blank href='#Form/Item/{0}'>{1}</a>".format(item.item_code, item.item_code)
			msg = "Kindly Update No. of Item can be packed Field for Item {0}".format(item_link)
			frappe.throw(msg)


	box = []
	total_craton_weight = []
	for boxes in doc.items:
		if not boxes.total_carton_weight_in_kg:
			boxes.total_carton_weight_in_kg = boxes.per_carton_weight_in_kg * boxes.carton_qty
		else:
			boxes.total_carton_weight_in_kg = boxes.total_carton_weight_in_kg 

		box.append(boxes.carton_qty)
		total_craton_weight.append(float(boxes.total_carton_weight_in_kg))
	doc.total_no_of_boxes = sum(box)
	doc.total_craton_weight = sum(total_craton_weight)

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
