# import frappe

# @frappe.whitelist()
# def get_data(item_code):

# 	print('/////////')
# 	print(item_code)
# 	print('/////////')
# 	item = frappe.db.sql(f"""SELECT dimension, per_carton_weight_kgs, isbn_code, book_binding, publish_date, publisher, books_per_carton, weight_per_unit,
# 								 weight_uom, book_language, book_size, author, about_book, no_of_pages
# 								 FROM `tabItem` 
# 								 WHERE item_code = '{item_code}' """, as_dict=1)
# 	#item_data = frappe.db.get_value("Item", item_code, ["dimension","per_carton_weight_in_kgs", "isbn_code",])

# 	print('///////////')
# 	print(item)
# 	print(item[0])
# 	print(item[0].get('no_of_pages'))
# 	print('///////////')
# 	return item
	# set_data(item, item_code)


# # def set_data(item, item_code):
#def vaildate(doc, method):
	# batch = frappe.get_doc('Batch', name)
	# batch.dimension = item[0].get('dimension'),
	# batch.per_carton_weight_kgs = item[0].get('per_carton_weight_kgs'),
	# batch.isbn_code = item[0].get('isbn_code'),
	# batch.book_binding = item[0].get('book_binding'),
	# batch.publish_date = item[0].get('publish_date'),
	# batch.publisher = item[0].get('publisher'),
	# batch.books_per_carton = item[0].get('books_per_carton'),
	# batch.weight_per_unit = item[0].get('weight_per_unit'),
	# batch.weight_uom = item[0].get('weight_uom'),
	# batch.book_language = item[0].get('book_language'),
	# batch.book_size = item[0].get('book_size'),
	# batch.author = item[0].get('author'),
	# batch.about_book = item[0].get('about_book'),
	# batch.no_of_pages = item[0].get('no_of_pages')

	# batch.insert()
	# frappe.db.commit()

# def before_save(doc, method):

# 		items = frappe.db.sql(f"""SELECT dimension, per_carton_weight_kgs, isbn_code, book_binding, publish_date, publisher, books_per_carton, weight_per_unit,
# 								 weight_uom, book_language, book_size, author, about_book, no_of_pages
# 								 FROM `tabItem` 
# 								 WHERE item_code = '{doc.item}' """, as_dict=1)

# 		print('/////////')
# 		print(items)
# 		print(doc.item)
# 		print(items[0].get('book_language'))
# 		print('/////////')

# 		# frappe.db.set_value('Batch', doc.item, {
# 		#     'dimension': items[0].get('dimension'),
# 		#     'per_carton_weight_in_kgs': items[0].get('per_carton_weight_kgs'),
# 		#     # 'no_of_pages': items[0].get('no_of_pages'),
# 		#     'weight_uom': items[0].get('weight_uom'),
# 		#     'book_language': items[0].get('book_language')
# 		# })

# 		batch = frappe.get_doc('Batch', doc.item)
# 		doc.dimension = items[0].get('dimension'),
# 		doc.per_carton_weight_kgs = items[0].get('per_carton_weight_kgs'),
# 		doc.isbn_code = items[0].get('isbn_code'),
# 		doc.book_binding = items[0].get('book_binding'),
# 		doc.publish_date = items[0].get('publish_date'),
# 		doc.publisher = items[0].get('publisher'),
# 		doc.books_per_carton = items[0].get('books_per_carton'),
# 		doc.weight_per_unit = items[0].get('weight_per_unit'),
# 		doc.weight_uom = items[0].get('weight_uom'),
# 		doc.book_language = items[0].get('book_language'),
# 		doc.book_size = items[0].get('book_size'),
# 		doc.author = items[0].get('author'),
# 		doc.about_book = items[0].get('about_book'),
# 		doc.no_of_pages = items[0].get('no_of_pages')

		# doc.reload()

		# doc.insert()
		#frappe.db.commit()


