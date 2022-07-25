frappe.ui.form.on("Address", {

	address_line1:function(frm) {

		frappe.call({
			method:'bbt_bpm.custom_script.address.address.address_links',
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
		
	}

});

// frappe.ui.form.on("Dynamic Link", {

// 	validate: function(frm,cdt,cdn){

// 		let row = locals[cdt][cdn];
// 		console.log('Hiii')

// 		frappe.call({
// 			method:'bbt_bpm.bbt_bpm.custom_script.address.address.address_links',
// 			// args:{
// 			// 	    'filters': {'user': frappe.session.user}
// 			//         //async: false
// 			// },
// 			callback: function(data){
// 				console.log('Hello');
// 				let d = data.message;
// 				console.log(d);
// 				// for(let i in d){
// 				// 	//console.log(i); // i = 0,1
// 				// 	//console.log(d[i]['weight_per_unit']);
// 				// 	//row.dimension = d[i]['dimension']
// 				// }
// 				// frm.refresh_fields("links");
// 			}
// 		})
// 	}

// })