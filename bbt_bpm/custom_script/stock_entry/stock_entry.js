frappe.ui.form.on("Stock Entry", {
	refresh: function(frm){
		if (frm.doc.sales_order_ref){
			frm.set_value("stock_entry_type", "Stock Reservation")
			frm.trigger("hide_add_delete_option")
		}

		if (frm.doc.quotation_ref) {
			frm.set_value("stock_entry_type", "Stock Reservation")
			frm.trigger("hide_add_delete_option")
		}
	},

	hide_add_delete_option: function(frm){
		$('[data-fieldname="items"]').find('.grid-buttons').hide()
		$('[data-fieldname="items"]').find('.grid-download').hide()
		$('[data-fieldname="items"]').find('.grid-upload').hide()
		$('[data-fieldname="items"]').find('.octicon-triangle-down').hide()
		$('[data-fieldname="items"]').find('.grid-add-row').hide()
		$('[data-fieldname="items"]').find('.grid-row-check').hide()
		$('[data-fieldname="items"]').find('.grid-remove-rows').hide()
		$('[data-fieldname="items"]').find('.grid-delete-row').hide()
		$('[data-fieldname="items"]').find('.grid-insert-row-below').hide()
		$('[data-fieldname="items"]').find('.grid-insert-row').hide()
		$('[data-fieldname="items"]').find('.grid-add-multiple-rows').hide()
	},

	items_on_form_rendered:function(frm,cdt,cdn){
		$('[data-fieldname="items"]').find('.close').hide()
		$('[data-fieldname="items"]').find('.grid-add-row').hide()
		$('[data-fieldname="items"]').find('.grid-row-check').hide()
		$('[data-fieldname="items"]').find('.grid-remove-rows').hide()
		$('[data-fieldname="items"]').find('.grid-delete-row').hide()
		$('[data-fieldname="items"]').find('.grid-insert-row-below').hide()
		$('[data-fieldname="items"]').find('.grid-insert-row').hide()
		$('[data-fieldname="items"]').find('.grid-append-row').hide()
		$('[data-fieldname="items"]').find('.grid-move-row').hide()
		$('[data-fieldname="items"]').find('.grid-duplicate-row').hide()
		$('[data-fieldname="items"]').find('.pull-right').hide()
		$('[data-fieldname="items"]').find('.text-muted').hide()
	}
})