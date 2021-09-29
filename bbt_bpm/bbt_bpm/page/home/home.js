frappe.pages['home'].on_page_load = function(wrapper) {
	wrapper.home = new frappe.Home({
		$wrapper: $(wrapper)
	});
}
frappe.Home  = Class.extend({
	init: function (opts) {
		this.$wrapper = opts.$wrapper
		this.filters = {}
		this.$wrapper.append(frappe.render_template("home", {}))
		$("#bbt-sidebar").append(frappe.render_template("sidebar_menu", {}));
		frappe.breadcrumbs.add("Bbt Bpm");
	},
	make: function() {
		var me = this;		
	}
});


