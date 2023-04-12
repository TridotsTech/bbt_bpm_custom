frappe.ui.form.on("Delivery Note", {
	refresh: function(frm){
		if (frappe.session.user != "Administrator" && frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}
	},
	delivery_confirmed:function(frm) {
		if (frm.doc.delivery_confirmed){
			frm.set_df_property('actual_delivered_date', 'reqd', 1);
		}
	}
});

frappe.ui.form.on("Delivery Note Item", {

	item_code: function(frm,cdt,cdn){

		let row = locals[cdt][cdn];
		let i_c = row.item_code;

		if(i_c){
			frappe.call({
				method:'frappe.client.get_list',
				args:{
						'doctype': 'Batch',
					    'filters': {'item': i_c},
					    'fields': [
				            'dimension',
				            'per_carton_weight_in_kgs',
				            'isbn_code',
				            'book_binding',
				            'publish_date',
				            'publisher',
				            'books_per_carton',
				            'weight_per_unit',
				            'weight_uom',
				            'no_of_pages',
				            'book_language',
				            'book_size',
				            'author',
				            'about_book'
				            ],
				        //async: false
				},
				callback: function(data){
					let d = data.message;
					for(let i in d){
						//console.log(i); // i = 0,1
						console.log(d[i]['weight_per_unit']);
						row.dimension = d[i]['dimension'], 
						row.per_carton_weight_in_kg = d[i]['per_carton_weight_in_kgs'],
						row.isbn_code = d[i]['isbn_code'],
						row.book_binding = d[i]['book_binding'],
						row.publish_date = d[i]['publish_date'],
						row.publisher = d[i]['publisher'],
						row.books_per_carton = d[i]['books_per_carton'],
						//frappe.model.set_value(cdt, cdn, 'weight_per_unit', d[i]['weight_per_unit']);
						row.book_weight_per_unit = d[i]['weight_per_unit'],
						//row.weight_uom = d[i]['weight_uom'],
						row.no_of_pages = d[i]['no_of_pages'],
						row.book_language = d[i]['book_language'],
						row.book_size = d[i]['book_size'],
						row.author = d[i]['author'],
						row.about_book = d[i]['about_book']
						console.log(row.weight_per_unit)
					}
					frm.refresh_fields("items");
				}
			})
		}

	}

});