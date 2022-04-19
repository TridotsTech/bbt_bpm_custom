frappe.ui.form.on("Batch", {

	item: function(frm){

		let item_code = frm.doc.item;
		console.log(item_code);
		//console.log(frm.doc);
		console.log(frm.doc.name);

		if (item_code){
			frappe.call({
				method:'frappe.client.get_list',
				args:{
						'doctype': 'Item',
					    'filters': {'name': item_code},
					    'fields': [
				            'dimension',
				            'per_carton_weight_kgs',
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
					//console.log(d[0]['book_language']);
					for(let i in d){
						//console.log(i); // i = 0
						//console.log(d[i]['book_language']);
						frm.set_value({
							dimension: d[i]['dimension'], 
							per_carton_weight_in_kgs: d[i]['per_carton_weight_kgs'],
							isbn_code: d[i]['isbn_code'],
							book_binding: d[i]['book_binding'],
							publish_date: d[i]['publish_date'],
							publisher: d[i]['publisher'],
							books_per_carton: d[i]['books_per_carton'],
							weight_per_unit: d[i]['weight_per_unit'],
							weight_uom: d[i]['weight_uom'],
							no_of_pages: d[i]['no_of_pages'],
							book_language: d[i]['book_language'],
							book_size: d[i]['book_size'],
							author: d[i]['author'],
							about_book: d[i]['about_book']

							})
					}
					//console.log(data.message.per_carton_weight_in_kgs);
					
				}
			})
		}
	}

})