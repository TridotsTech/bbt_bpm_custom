frappe.ui.form.on("Sales Order", {
	onload: function(frm){
		frm.trigger("hide_sidebar")
		frm.trigger("map_on_stock_entry")
	},
	refresh: function(frm){
		frm.trigger("hide_sidebar")
		frm.trigger("map_on_stock_entry")

		frm.add_custom_button(__('Duplicate'), function() {           
                var new_so = frappe.model.copy_doc(frm.doc);
                frappe.set_route('Form', 'Sales Order', new_so.name);
            });
		
		if (frappe.session.user != "Administrator" && frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}

		frm.add_custom_button(__('Split Sales Order'), function() {
				frappe.call({
					method:'bbt_bpm.custom_script.sales_order.sales_order.split_so',
					args:{
						doc: frm.doc,
						method:'bbt_bpm.custom_script.sales_order.sales_order.split_so'
						},
				callback: function(data){
					console.log(data,'-----')
					// var d = data.message;
					}
				})
            });
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
	