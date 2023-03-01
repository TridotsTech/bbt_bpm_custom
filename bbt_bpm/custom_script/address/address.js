frappe.ui.form.on("Address", {

	address_line1:function(frm) {

		frappe.call({
			method:'bbt_bpm.custom_script.address.address.address_links',
			args:{user: frappe.session.user},
			callback: function(data){
				var d = data.message;
				if (frappe.session.user != 'Administrator'){
					for (var i = 0; i < d.length-1; i++){
					var childTable = frm.add_child("links");
					childTable.link_doctype = d[0];
					childTable.link_name = d[1];
				
				} 
			}
				
				frm.refresh_fields("links");
			}
			// frm.refresh_fields("links"); frm not getting loaded
		})
		// frm.clear_table("links"); CT getting populated but not reflecting
		
	},
	refresh: function(frm){
		if (frappe.session.user != "Administrator" && frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}

		if (frappe.session.user != "Administrator"){
			set_field_options("address_type", 'Shipping');
		}
	}

});

