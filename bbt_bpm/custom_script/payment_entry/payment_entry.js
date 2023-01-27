frappe.ui.form.on("Payment Entry", {
	refresh: function(frm){
		if (frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}
	}

});