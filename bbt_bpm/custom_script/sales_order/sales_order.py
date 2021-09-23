from __future__ import unicode_literals
from re import sub
import frappe
from frappe.utils import cint, cstr,flt
import json
from frappe.model.mapper import get_mapped_doc
import math
import re

def validate(doc, method):

    for row in doc.items:
        doc.stock_transfer_ref=frappe.db.get_value("Stock Entry", {"quotation_ref":row.prevdoc_docname, "docstatus":1}, "name")		
        outstanding_amount = frappe.db.sql("""SELECT sum(outstanding_amount) as amount from `tabSales Invoice` where customer='{0}' and company='{1}' and docstatus=1 """.format(doc.customer, doc.company), as_dict=1)
        if outstanding_amount[0]:
            doc.outstanding_amount = outstanding_amount[0].get('amount')
    set_field_value(doc)

def before_save(doc, method):
    set_packaging_items(doc)
    set_item_warehouses(doc)
    set_valid_customer_warehouse(doc)   

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
            # if is_packaging in ["Carton","packaging material"]:
            #     continue
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

    if final_warehouse:
        frappe.db.set_value("Sales Order",doc.name,"set_warehouse",final_warehouse)
        doc.set_warehouse=final_warehouse
    else:
        frappe.db.set_value("Sales Order",doc.name,"set_warehouse",frappe.db.get_value("Stock Settings", "Stock Settings", 'default_warehouse' ))
        doc.set_warehouse=frappe.db.sql(""" SELECT value from `tabSingles` where doctype='Stock Settings' and field='default_warehouse' """)[0]
    
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
    print(actual_qty, item)
    return actual_qty
    

def set_field_value(doc):
    doc.credit_limit=frappe.db.get_value("Customer Credit Limit",{"parent":doc.customer,"company":doc.company},"credit_limit")


def set_packaging_items(doc):
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
    delivery_date=doc.items[0].delivery_date

    for item in doc.items:
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
            soi.delivery_date=delivery_date
            soi.qty=math.ceil(qty)
            soi.rate=rate
            soi.amount=flt(rate)*flt(math.ceil(qty))
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
        frappe.db.set_value("Sales Order Item", item.name, "warehouse", doc.set_warehouse)
    