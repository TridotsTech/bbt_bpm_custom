frappe.ui.form.on("Quotation", {
	onload: function(frm){
		frm.trigger("hide_add_delete_option")
	},
	refresh: function(frm){
		frm.trigger("map_on_stock_entry")
	},
	map_on_stock_entry: function(frm){
		frm.add_custom_button(__('Stock Block'), function() {
			frappe.confirm("Are you sure you want to a create Stock Block Entry",function(){
				frappe.model.open_mapped_doc({
					method: "bbt_bpm.custom_script.quotation.quotation.map_on_stock_entry",
					frm: cur_frm
				})
			})
		});
	}
})