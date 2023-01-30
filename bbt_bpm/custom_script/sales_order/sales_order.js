frappe.ui.form.on("Sales Order", {
	onload: function(frm){
		frm.trigger("hide_sidebar")
		frm.trigger("map_on_stock_entry")
	},
	refresh: function(frm){
		frm.trigger("hide_sidebar")
		frm.trigger("map_on_stock_entry")
		
		if (frappe.session.user != "Administrator" && frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}
	},
	map_on_stock_entry: function(frm){
		if (frm.doc.docstatus==0 && !frm.doc.stock_transfer_ref){
			frm.add_custom_button(__('Stock Block'), function() {
				frappe.confirm("Are you sure you want to a create Stock Entry",function(){
					frappe.model.open_mapped_doc({
						method: "bbt_bpm.custom_script.sales_order.sales_order.map_on_stock_entry",
						frm: cur_frm
					})
				})
			});
		}
	},

	hide_sidebar: function(frm){
		if ((frappe.session.user !="Administrator") && frappe.user.has_role(["Customer"])){
			$(".form-sidebar").css("display", "none");
		}
	}	
})
	