frappe.ui.form.on("Sales Order", {
	refresh: function(frm){
		frm.trigger("map_on_stock_entry")
	},

	map_on_stock_entry: function(frm){
		frappe.db.get_value("Delivery Note Item", {"against_sales_order": frm.doc.name}, "parent", (r) => {
			if ( !r.parent && !frm.doc.__islocal && frm.doc.docstatus != 1 && !frm.doc.stock_transfer_ref ){
				frm.add_custom_button(__('Stock Block'), function() {
					frappe.confirm("Are you sure you want to a create Stock Entry",function(){
						frappe.model.open_mapped_doc({
							method: "bbt_bpm.custom_script.sales_order.sales_order.map_on_stock_entry",
							frm: cur_frm
						})
					})
				});
			}
		}, 'Delivery Note');
	}
})