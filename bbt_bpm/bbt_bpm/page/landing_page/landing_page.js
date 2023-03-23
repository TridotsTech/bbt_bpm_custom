// frappe.pages['landing_page'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'None',
// 		single_column: true
// 	});
// }


frappe.pages['landing_page'].on_page_load = function(wrapper) {
	wrapper.landing_page = new frappe.landing_page({
		$wrapper: $(wrapper)
	});
}
frappe.landing_page  = Class.extend({
	init: function (opts) {
		this.$wrapper = opts.$wrapper
		this.filters = {}
		this.$wrapper.append(frappe.render_template("landing_page", {}))
		$("#bbt-sidebar").append(frappe.render_template("sidebar_menu", {}));
		frappe.breadcrumbs.add("Bbt Bpm");
	},
	make: function() {
		var me = this;		
	}
});


