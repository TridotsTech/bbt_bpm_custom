from __future__ import unicode_literals
from re import sub
import frappe
from frappe.utils import cint, cstr,flt
import json
from frappe.model.mapper import get_mapped_doc
import math
import re
from frappe import _, msgprint, scrub
from frappe.utils import has_common
from datetime import date
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

def validate(doc, method):
    person_data = frappe.db.get_value("Contact",{"name":doc.contact_person},['phone','mobile_no','first_name','last_name'],as_dict=True)
    # contact_display = person_data.get('first_name') + " " + person_data.get('last_name') or " "
    if person_data.get('phone'):
        doc.contact_phone = person_data.get('phone') or ""
    if person_data.get('mobile_no'):
        doc.contact_mobile = person_data.get('mobile_no') or ""
    if person_data.get('first_name') and not person_data.get('last_name'):
        contact_display = person_data.get('first_name')
        doc.contact_display = contact_display
    elif person_data.get('first_name') and person_data.get('last_name'):
        contact_display = person_data.get('first_name') + " " + person_data.get('last_name')
        doc.contact_display = contact_display
   
    for row in doc.items:
        if frappe.db.exists("Stock Entry", {"quotation_ref":row.prevdoc_docname, "docstatus":1}):
            doc.stock_transfer_ref=frappe.db.get_value("Stock Entry", {"quotation_ref":row.prevdoc_docname, "docstatus":1}, "name")		
        outstanding_amount = frappe.db.sql("""SELECT sum(outstanding_amount) as amount from `tabSales Invoice` where customer='{0}' and company='{1}' and docstatus=1 """.format(doc.customer, doc.company), as_dict=1)
        if outstanding_amount[0]:
            doc.outstanding_amount = outstanding_amount[0].get('amount')

        row.delivery_date = doc.delivery_date
    
    set_field_value(doc)
    set_packaging_items(doc)
    set_valid_customer_warehouse(doc)
    set_item_warehouses(doc)
    sort_table(doc)


def on_update(doc, method):
    rm_unwanted_items(doc)

def on_submit(doc, method):
    for row in doc.items:
        if doc.stock_transfer_ref:

            allocated_qty = frappe.db.sql("""select sum(qty) from `tabSales Order Item` soi join 
            `tabWarehouse` w on soi.warehouse=w.name where soi.item_code=%(item_code)s and soi.docstatus=1 
            and w.is_reserved=1""", {"item_code":row.item_code})
            

            delivered_qty = frappe.db.sql("""select sum(qty) from `tabDelivery Note Item` soi join `tabWarehouse` w on soi.warehouse=w.name 
            where soi.item_code=%(item_code)s and soi.docstatus=1 and w.is_reserved=1""", {"item_code":row.item_code}) 
            

            if allocated_qty[0][0] == None:
                allocated_qty_1 = 0
            else:
                allocated_qty_1 = allocated_qty[0][0]

            if delivered_qty[0][0] == None:
                delivered_qty_1 = 0
            else:
                delivered_qty_1 = delivered_qty[0][0]

            actual_allocated_qty = allocated_qty_1 - delivered_qty_1

            
            frappe.db.set_value("Item", row.item_code, "allocated_qty", actual_allocated_qty)


def set_valid_customer_warehouse(doc):
    if frappe.db.exists("Warehouse", {"name":doc.set_warehouse, "is_reserved":1}):
        return
    customer_wahouses=frappe.db.get_value("Customer",doc.customer,["primary_warehouse","secondary_warehouse","ternary_warehouse"],as_dict=1)
    final_warehouse=None

    for warehouse in customer_wahouses.values():
        if final_warehouse:
            continue

        is_err=False
        for item in doc.items:
            is_packaging=frappe.db.get_value("Item",item.item_code,"item_group")
            item_available=check_stock_availability(item.item_code,warehouse)
            if not item_available[0]:
                is_err = True
                break
            if is_err or not item_available[0]:
                is_err=True
                break
            elif not item_available[0]>=item.qty:
                is_err=True
                break
            elif item_available[0]>item.qty:
                continue

        if is_err:
            continue
        else:
            final_warehouse=warehouse
    
    if final_warehouse and doc.company != "Bhaktivedanta Book Trust":
        return
    if final_warehouse and doc.company == "Bhaktivedanta Book Trust":
        doc.set_warehouse=final_warehouse
    else:
        if doc.company != "Bhaktivedanta Book Trust":
            return
        else:
            doc.set_warehouse=frappe.db.get_value("Stock Settings","Stock Settings","default_warehouse")
    
def check_stock_availability(item,warehouse):
    actual_qty=frappe.db.sql_list("""SELECT
                                        SUM(actual_qty)
                                    FROM
                                        `tabBin`
                                    WHERE
                                        item_code=%(item)s
                                    AND
                                        warehouse=%(warehouse)s
                                    """,{"item":item,"warehouse":warehouse})
    return actual_qty
    

def set_field_value(doc):
    doc.credit_limit=frappe.db.get_value("Customer Credit Limit",{"parent":doc.customer,"company":doc.company},"credit_limit")
    
    
    #customer_credit_limit = frappe.db.get_value('Customer Credit Limit', {"parent":doc.customer,"company":doc.company}, 'credit_limit')
    customer = frappe.db.get_value('Customer', doc.customer, 'customer_name') 
    out_amount = frappe.db.sql("""SELECT outstanding_amount FROM `tabSales Invoice` 
                                WHERE customer = %(customer)s""",{"customer":customer}, as_dict = 1)

    total_unpaid = 0
    for i in range(len(out_amount)):
        total_unpaid += out_amount[i]['outstanding_amount'] 

    if doc.credit_limit: # Is none if custom credit limit not set
        if int(total_unpaid) > int(doc.credit_limit):
            #frappe.db.set_value('Sales Order', doc.credit_limit_ex, 'CLE' )
            doc.credit_limit_ex = 'CLE'
        else:
            #frappe.db.set_value('Sales Order', doc.credit_limit_ex, '' )
            doc.credit_limit_ex = ''


def set_packaging_items(doc):
    if doc.edit_carton_items == 1:
        return
    po_items=[]
    remove_items=[]
    for i in doc.items: 
        is_packaging=frappe.db.get_value("Item",i.item_code,"item_group")
        if is_packaging in ["Carton","packaging material"]:
            frappe.db.sql("DELETE FROM `tabSales Order Item` WHERE name=%(name)s",{"name":i.name})
            remove_items.append(i)
            continue
        po_items.append(i)

    for i in remove_items:
        doc.items.remove(i)

    sub_item_ind=len(doc.items)

    for item in doc.items:
        # exe_qty = frappe.db.get_value("Sales Order Item", i.name, "qty")
        # is_packaging=frappe.db.get_value("Item",i.item_code,"item_group")
        # if is_packaging in ["Carton","packaging material"] and exe_qty == i.qty:
        #     continue    
        is_packaging_item=frappe.db.get_value("Item",item.item_code,"no_of_items_can_be_packed")
        is_catorn_req=frappe.db.get_value("Item",item.item_code,"carton")
        if is_packaging_item:
            qty=item.qty/is_packaging_item
            if item.quantity_carton and doc.calculate_quantity_from_carton:
                item.qty = item.quantity_carton * is_packaging_item
            else:
                item.quantity_carton = math.ceil(item.qty / is_packaging_item)
        if is_packaging_item and is_catorn_req:
            packing_item_code=frappe.db.get_value("Item",item.item_code,"carton")
            item_doc=frappe.get_cached_doc("Item",packing_item_code)
            qty=item.qty/is_packaging_item
            item.quantity_carton = math.ceil(item.qty / is_packaging_item)
            # if item.quantity_carton:
            #     item.qty = item.quantity_carton * is_packaging_item
            # else:
            # item.quantity_carton = math.ceil(item.qty / is_packaging_item)    
            conversion_factor=frappe.db.get_value("UOM Conversion Detail",{"parent":item_doc.item_code,"uom":item_doc.sales_uom},"conversion_factor")
            rate=frappe.db.get_value("Item Price",{"item_code":item_doc.item_code,"price_list":doc.selling_price_list},"price_list_rate")
            if not conversion_factor:
                conversion_factor=1

            # Adds a row(2nd) for items having carton
            soi=frappe.new_doc("Sales Order Item")
            soi.parenttype="Sales Order"
            soi.parentfield="items"
            soi.item_code=item_doc.item_code
            soi.item_name=item_doc.item_name
            soi.description=item_doc.description
            soi.delivery_date=doc.delivery_date
            soi.qty=math.ceil(qty)
            #soi.quantity_carton = is_packaging_item / int(soi.qty)
            soi.is_free_item = 1
            soi.rate = 0
            # soi.amount=flt(rate)*flt(math.ceil(qty))
            soi.amount = 0
            soi.uom=item_doc.sales_uom
            soi.stock_uom=item_doc.stock_uom
            
            soi.conversion_factor=conversion_factor
            soi.stock_qty=conversion_factor*math.ceil(qty)
            soi.idx=sub_item_ind+1
            soi.parent=doc.name
            po_items.append(soi)
            sub_item_ind+=1
            soi.insert(ignore_permissions = True)
            soi.save()
        # elif not is_packaging_item:
        #     item_link="<a target=_blank href='#Form/Item/{0}'>{1}</a>".format(item.item_code,item.item_code)
        #     msg="Kindly Update No. of Item can be packed Field for Item {0}".format(item_link)
        #     frappe.throw(msg)

    doc.items=po_items


@frappe.whitelist()
def map_on_stock_entry(source_name, target_doc=None):
	stock_entry_types="Stock Reservation"
	target_doc = get_mapped_doc("Sales Order", source_name,
		{"Sales Order": {
		"doctype": "Stock Entry",
		"field_map": {
			"company": "company",
			"name": "sales_order_ref",
			"set_warehouse": "from_warehouse",
			"stock_entry_type": "Stock Reservation"
			}
		},
		"Sales Order Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"warehouse": "s_warehouse",
				"transfer_qty": "qty",
			},
		}
	})
	return target_doc


def set_item_warehouses(doc):
        for item in doc.items:
            if not doc.edit_item_warehouse:
                item.warehouse=doc.set_warehouse
            else:
                doc.set_warehouse=item.warehouse

def rm_unwanted_items(doc):
    db_items=frappe.db.sql(""" select item_code, warehouse,projected_qty,name from `tabSales Order Item` where parent=%(doc_name)s """,{"doc_name":doc.name},as_dict=1)
    doc_itm_name=[soi.name for soi in doc.items]
    for rm_item in db_items:
        if rm_item.name not in doc_itm_name:
            frappe.db.sql("DELETE FROM `tabSales Order Item` WHERE name=%(name)s",{"name":rm_item.name})


def sort_table(doc):
    # built-in function that return a list of (index, item) of a given list of objects, `start` is a parameter to define the first value of the index
    # `key` to get the value to be used in the sort comparization.
    for i, item in enumerate(sorted(doc.items, key=lambda item: (frappe.db.get_value("Item",{"item_code":item.item_code},"book_language"), item.item_name)), start=1):
        item.idx = i # define the new index to the object based on the sorted order



#------------------------------------------------------------------
#Permission Query
#------------------------------------------------------------------
def so_get_permission_query_conditions(user):
    if not user: user = frappe.session.user

    cust = frappe.db.get_value("Customer", {"user":user}, "name")
    orders=frappe.db.sql("""select name from `tabSales Order` where customer='{0}' """.format(cust), as_dict=1) 
    so_list = [ '"%s"'%so.get("name") for so in orders ]

    roles = frappe.get_roles();
    if user != "Administrator" and has_common(['Customer'],roles) :
        if so_list:
            return """(`tabSales Order`.name in ({0}) )""".format(','.join(so_list))
        else:
            # return "1=2"
            return """(`tabSales Order`.name is null)"""

# @frappe.whitelist()
# def validate_warehouse():
#     #pass
# 		super(SalesOrder, self).validate_warehouse()

# 		for d in self.get("items"):
# 			if (frappe.get_cached_value("Item", d.item_code, "is_stock_item") == 1 or
# 				(self.has_product_bundle(d.item_code) and self.product_bundle_has_stock_item(d.item_code))) \
# 				and not d.warehouse and not cint(d.delivered_by_supplier):
# 				frappe.throw(_("stock item {0}").format(d.item_code),
# 					WarehouseRequired)

@frappe.whitelist()
def validate_warehouse(self):
    #pass
        super(SalesOrder, self).validate_warehouse()

        for d in self.get("items"):
            if (frappe.get_cached_value("Item", d.item_code, "is_stock_item") == 0 or
                (self.has_product_bundle(d.item_code) and self.product_bundle_has_stock_item(d.item_code))) \
                and not d.warehouse and not cint(d.delivered_by_supplier):
                frappe.throw(_("stock item {0}").format(d.item_code),
                    WarehouseRequired)
SalesOrder.validate_warehouse=validate_warehouse



@frappe.whitelist()
def split_so(doc,method):
    doc = json.loads(doc)
    so_split = []
    warehouse_data = {}

    split_so_name = frappe.db.sql(""" SELECT name from`tabSales Order` where sales_order_reference = '{}' """.format(doc.get('name')),as_dict=True)

    if split_so_name:
        for so in split_so_name:
            so_split.append(so.get('name'))

    if so_split:
        frappe.throw(f"Sales Order is already splited.The splited sales order is {so_split}")

    else:    
        for item in doc.get('items'):
            if item['warehouse'] not in warehouse_data:
                warehouse_data[item['warehouse']] = []
            warehouse_data[item['warehouse']].append(item)

        for wrh,data in warehouse_data.items():
            if wrh:
                if wrh == doc.get('from_warehouse'):
                    continue
                print(wrh,data)
                newdoc = frappe.new_doc('Sales Order')
                newdoc.customer = doc.get('customer')
                newdoc.company = doc.get('company')
                newdoc.delivery_date = doc.get('delivery_date')
                newdoc.transaction_date = doc.get('transaction_date')
                newdoc.order_type = doc.get('order_type')
                newdoc.order_class = doc.get('order_class')
                newdoc.submitted_date = doc.get('submitted_date')
                newdoc.request_no = doc.get('request_no')
                newdoc.credit_limit = doc.get('credit_limit')
                newdoc.accepted_by_warehouse = doc.get('accepted_by_warehouse')
                newdoc.outstanding_amount = doc.get('outstanding_amount')
                newdoc.booking_to_be_done_in_the_name_of = doc.get('booking_to_be_done_in_the_name_of')
                newdoc.po_no = doc.get('po_no')
                newdoc.delivery_contact_person_pan_no_or_gst_no = doc.get('delivery_contact_person_pan_no_or_gst_no')
                newdoc.stock_transfer_request_no = doc.get('stock_transfer_request_no')
                newdoc.stock_transfer_ref = doc.get('stock_transfer_ref')
                newdoc.delivery_type = doc.get('delivery_type')
                newdoc.credit_limit_ex = doc.get('credit_limit_ex')
                newdoc.payment = doc.get('payment')

                # address and contact section
                newdoc.sales_order_reference = doc.get('name')
                newdoc.customer_address = doc.get('customer_address')
                newdoc.shipping_address_name = doc.get('shipping_address_name')
                newdoc.billing_address_gstin = doc.get('billing_address_gstin')
                newdoc.customer_gstin = doc.get('customer_gstin')
                newdoc.address_display = doc.get('address_display')
                newdoc.place_of_supply = doc.get('place_of_supply')
                newdoc.territory = doc.get('territory')
                newdoc.contact_person = doc.get('contact_person') or ""
                newdoc.contact_display = doc.get('contact_display') or ""
                newdoc.contact_phone = doc.get('contact_phone') or ""
                newdoc.company_address = doc.get('company_address') or ""

                # currency and price list section
                newdoc.currency = doc.get('currency')
                newdoc.selling_price_list = doc.get('selling_price_list')
                newdoc.ignore_pricing_rule = doc.get('ignore_pricing_rule')
                # warehouse
                newdoc.set_warehouse = wrh
                newdoc.edit_item_warehouse = True
                newdoc.scan_barcode = doc.get('scan_barcode')
                newdoc.edit_carton_items = doc.get('edit_carton_items')
                newdoc.calculate_quantity_from_carton = doc.get('calculate_quantity_from_carton')
               
                for row in data:
                    frappe.db.delete('Sales Order Item', row.get('name'))
                    newdoc.append('items', {
                        'item_code': row.get('item_code'),
                        'delivery_date': row.get('delivery_date'),
                        'ensure_delivery_based_on_produced_serial_no':row.get('ensure_delivery_based_on_produced_serial_no'),
                        'item_name':row.get('item_name'),
                        'description':row.get('description'),
                        'qty': row.get('qty'),
                        'uom':row.get('uom'),
                        'quantity_carton':row.get('quantity_carton'),
                        'conversion_factor':row.get('conversion_factor'),
                        'stock_uom':row.get('stock_uom'),
                        'stock_qty':row.get('stock_qty'),
                        'price_list_rate':row.get('price_list_rate'),
                        'margin_type':row.get('margin_type'),
                        'discount_percentage':row.get('discount_percentage'),
                        'margin_rate_or_amount':row.get('margin_rate_or_amount'),
                        'discount_amount':row.get('discount_amount'),
                        'is_free_item':row.get('is_free_item'),
                        'rate': row.get('rate'),
                        'amount':row.get('amount'),
                        'item_tax_template':row.get('item_tax_template'),
                        'warehouse':row.get('warehouse'),
                        'billed_amt':row.get('billed_amt'),
                        'valuation_rate':row.get('valuation_rate'),
                        'gross_profit':row.get('gross_profit'),
                        'delivered_by_supplier':row.get('delivered_by_supplier'),
                        'supplier':row.get('supplier'),
                        'weight_per_unit':row.get('weight_per_unit'),
                        'total_weight':row.get('total_weight'),
                        'weight_uom':row.get('weight_uom'),
                        'blanket_order':row.get('blanket_order'),
                        'blanket_order_rate':row.get('blanket_order_rate'),
                        'projected_qty':row.get('projected_qty'),
                        'actual_qty':row.get('actual_qty'),
                        'ordered_qty':row.get('ordered_qty'),
                        'work_order_qty':row.get('work_order_qty'),
                        'delivered_qty':row.get('delivered_qty'),
                        'additional_notes':row.get('additional_notes'),
                        'page_break':row.get('page_break')
                    })
                # total calculation
                # newdoc.total_qty = doc.get('total_qty')
                # newdoc.total_net_weight = doc.get('total_net_weight')
                # newdoc.total = doc.get('total')

                # transporter information
                newdoc.transporter = doc.get('transporter')
                newdoc.gst_transporter_id = doc.get('gst_transporter_id')
                newdoc.driver = doc.get('driver')
                newdoc.transport_receipt_no = doc.get('transport_receipt_no')
                newdoc.vehicle_no = doc.get('vehicle_no')
                newdoc.special_instruction = doc.get('special_instruction')
                newdoc.unloading_instruction = doc.get('unloading_instruction')
                newdoc.distance_in_km = doc.get('distance_in_km')
                newdoc.transporter_delivery_branch = doc.get('transporter_delivery_branch')
                newdoc.transporter_delivery_branch_contact_number = doc.get('transporter_delivery_branch_contact_number')
                newdoc.mode_of_transport = doc.get('mode_of_transport')
                newdoc.transport_receipt_date = doc.get('transport_receipt_date')
                newdoc.gst_vehicle_type = doc.get('gst_vehicle_type')
                newdoc.preferred_transporter = doc.get('preferred_transporter')
                newdoc.instruction_for_delivery = doc.get('instruction_for_delivery')
                
                # Taxes and Charges
                newdoc.tax_category = doc.get('tax_category')
                newdoc.shipping_rule = doc.get('shipping_rule')
                newdoc.taxes_and_charges = doc.get('taxes_and_charges')
                
                # Tax Breakup
                newdoc.other_charges_calculation = doc.get('other_charges_calculation')
                newdoc.base_total_taxes_and_charges = doc.get('base_total_taxes_and_charges')
                newdoc.total_taxes_and_charges = doc.get('total_taxes_and_charges')
                
                # Loyalty Points Redemption
                newdoc.loyalty_points = doc.get('loyalty_points')
                newdoc.loyalty_amount = doc.get('loyalty_amount')
                newdoc.coupon_code = doc.get('coupon_code')
                newdoc.apply_discount_on = doc.get('apply_discount_on')
                newdoc.base_discount_amount = doc.get('base_discount_amount')
                newdoc.additional_discount_percentage = doc.get('additional_discount_percentage')
                newdoc.discount_amount = doc.get('discount_amount')
                newdoc.base_grand_total = doc.get('base_grand_total')
                newdoc.base_rounding_adjustment = doc.get('base_rounding_adjustment')
                newdoc.base_rounded_total = doc.get('base_rounded_total')
                newdoc.base_in_words = doc.get('base_in_words')
                newdoc.grand_total = doc.get('grand_total')
                newdoc.rounding_adjustment = doc.get('rounding_adjustment')
                newdoc.rounded_total = doc.get('rounded_total')
                newdoc.in_words = doc.get('in_words')
                newdoc.advance_paid = doc.get('advance_paid')

                # Packing List
                newdoc.payment_terms_template = doc.get('payment_terms_template')

                #Terms and Conditions
                newdoc.tc_name = doc.get('tc_name')
                newdoc.terms = doc.get('terms')

                # More Information
                newdoc.inter_company_order_reference = doc.get('inter_company_order_reference')
                newdoc.project = doc.get('project')
                newdoc.party_account_currency = doc.get('party_account_currency')
                newdoc.source = doc.get('source')
                newdoc.campaign = doc.get('campaign')

                # Print Settings
                newdoc.language = doc.get('language')
                newdoc.letter_head = doc.get('letter_head')
                newdoc.select_print_heading = doc.get('select_print_heading')
                newdoc.group_same_items = doc.get('group_same_items')

                # Billing and Delivery Status
                newdoc.status = doc.get('status')
                newdoc.delivery_status = doc.get('delivery_status')
                newdoc.per_delivered = doc.get('per_delivered')
                newdoc.per_billed = doc.get('per_billed')
                newdoc.billing_status = doc.get('billing_status')

                # Commission
                newdoc.sales_partner = doc.get('sales_partner')
                newdoc.commission_rate = doc.get('commission_rate')
                newdoc.total_commission = doc.get('total_commission')

                # Auto Repeat Section
                newdoc.from_date = doc.get('from_date')
                newdoc.to_date = doc.get('to_date')
                newdoc.auto_repeat = doc.get('auto_repeat')

                newdoc.save(ignore_permissions=True)
            # frappe.db.commit()
            # frappe.db.delete('Sales Order', doc.get('name'))

        frappe.msgprint('Sales Order splited successfully');