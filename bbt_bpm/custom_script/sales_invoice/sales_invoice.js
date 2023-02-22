frappe.ui.form.on("Sales Invoice", {
	onload: function(frm){
		frm.trigger("hide_sidebar")
	},
	refresh: function(frm){
		frm.trigger("hide_sidebar")
		if (frappe.session.user != "Administrator" && frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}
	},

	hide_sidebar: function(frm){
		if ((frappe.session.user !="Administrator") && frappe.user.has_role(["Customer"])){
			$(".form-sidebar").css("display", "none");
		}
	}	
})
	