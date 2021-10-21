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

def validate(doc, method):
    for row in doc.items:
        if frappe.db.exists("Stock Entry", {"quotation_ref":row.prevdoc_docname, "docstatus":1}):
            doc.stock_transfer_ref=frappe.db.get_value("Stock Entry", {"quotation_ref":row.prevdoc_docname, "docstatus":1}, "name")		
        outstanding_amount = frappe.db.sql("""SELECT sum(outstanding_amount) as amount from `tabSales Invoice` where customer='{0}' and company='{1}' and docstatus=1 """.format(doc.customer, doc.company), as_dict=1)
        if outstanding_amount[0]:
            doc.outstanding_amount = outstanding_amount[0].get('amount')
    set_field_value(doc)
    set_packaging_items(doc)
    set_valid_customer_warehouse(doc)
    set_item_warehouses(doc)

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
        if is_packaging_item and is_catorn_req:
            packing_item_code=frappe.db.get_value("Item",item.item_code,"carton")
            item_doc=frappe.get_cached_doc("Item",packing_item_code)
            qty=item.qty/is_packaging_item
            conversion_factor=frappe.db.get_value("UOM Conversion Detail",{"parent":item_doc.item_code,"uom":item_doc.sales_uom},"conversion_factor")
            rate=frappe.db.get_value("Item Price",{"item_code":item_doc.item_code,"price_list":doc.selling_price_list},"price_list_rate")
            if not conversion_factor:
                conversion_factor=1

            soi=frappe.new_doc("Sales Order Item")
            soi.parenttype="Sales Order"
            soi.parentfield="items"
            soi.item_code=item_doc.item_code
            soi.item_name=item_doc.item_name
            soi.description=item_doc.description
            soi.delivery_date=doc.delivery_date
            soi.qty=math.ceil(qty)
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
        elif not is_packaging_item:
            item_link="<a target=_blank href='#Form/Item/{0}'>{1}</a>".format(item.item_code,item.item_code)
            msg="Kindly Update No. of Item can be packed Field for Item {0}".format(item_link)
            frappe.throw(msg)

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
        item.warehouse=doc.set_warehouse

def rm_unwanted_items(doc):
    db_items=frappe.db.sql(""" select item_code, warehouse,projected_qty,name from `tabSales Order Item` where parent=%(doc_name)s """,{"doc_name":doc.name},as_dict=1)
    doc_itm_name=[soi.name for soi in doc.items]
    for rm_item in db_items:
        if rm_item.name not in doc_itm_name:
            frappe.db.sql("DELETE FROM `tabSales Order Item` WHERE name=%(name)s",{"name":rm_item.name})








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