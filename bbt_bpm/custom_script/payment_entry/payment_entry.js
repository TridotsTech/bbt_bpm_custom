frappe.ui.form.on("Payment Entry", {
	refresh: function(frm){
		if (frappe.session.user != "Administrator" && frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}
	}

});