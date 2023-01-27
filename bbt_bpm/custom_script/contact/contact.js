frappe.ui.form.on("Contact", {

	first_name:function(frm) {

		frappe.call({
			method:'bbt_bpm.custom_script.contact.contact.contact_links',
			args:{user: frappe.session.user},
			callback: function(data){
				var d = data.message;
				for (var i = 0; i < d.length-1; i++){
					var childTable = frm.add_child("links");
					childTable.link_doctype = d[0];
					childTable.link_name = d[1];
				
				} 
				frm.refresh_fields("links");
			}
			// frm.refresh_fields("links"); frm not getting loaded
		})
		// frm.clear_table("links"); CT getting populated but not reflecting
		
	},
	refresh: function(frm){
		if (frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}
	}

});