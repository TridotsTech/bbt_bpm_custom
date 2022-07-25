//frappe.ui.form.on("Pick List", {

// 		// get_item_locations: function(frm) {
// 	 //        $.each(frm.doc.locations, function(i,v) {
// 	 //                frappe.call({
// 	 //                    method: 'frappe.client.get_value',
// 	 //                    args: {
// 	 //                        'doctype': 'Item',
// 	 //                        'filters': {'name': v.item_code},
// 	 //                        'fieldname': [
// 	 //                            'no_of_items_can_be_packed'
// 	 //                        ]
// 	 //                    },
// 	 //                    callback: function(r) {
// 	 //                        if (!r.exc) {
// 	 //                            frappe.model.set_value(v.Pick List, v.name, "no_of_items_can_be_packed",r.message.no_of_items_can_be_packed);                                    
// 	 //                            frappe.model.set_value(v.Pick List, v.name, "qty",v.no_of_items_can_be_packed);                                    
	                            
// 	 //                        }
// 	 //                    }
// 	 //                });
// 	 //        });
//   //  }

// 		// before_save:function(frm){
// 		// 	//frm.add_custom_button( __("Create row"), function(){
// 		// 		for(let row of frm.doc.locations){
// 	 // 				let remaining_qty = row.qty - row.no_of_items_can_be_packed
// 	 // 				if (row.qty > row.no_of_items_can_be_packed){

// 	 // 					var d = frm.add_child("locations");
// 	 // 					d.item_code = row.item_code
// 	 // 					d.description = row.description
// 	 // 					d.item_name = row.item_name
// 	 // 					d.item_group = row.item_group
// 	 // 					d.warehouse = row.warehouse
// 	 // 					d.qty = remaining_qty
// 	 // 					d.stock_qty = remaining_qty
// 	 // 					d.picked_qty = remaining_qty
// 	 // 					d.no_of_items_can_be_packed = row.no_of_items_can_be_packed
// 	 // 					d.uom = row.uom
// 	 // 					d.conversion_factor = row.conversion_factor
// 	 // 					d.stock_uom = row.stock_uom 
// 	 // 					d.carton_no = row.carton_qty + '-' + remaining_qty
// 	 // 					d.carton_qty = 0

// 	 // 				};
	 				
// 		// 		};

// 		// 		frm.refresh_fields("locations");
// 				//frappe.db.commit();
// 				//frm.save()

				
// 		//});
// 	//}
	
    
//   //   after_save:function(frm){
//   //       // var SO = frm.doc.locations[0].sales_order    
//   //       // console.log(frm.doc.locations[0].sales_order)
//   //       // if (frm.doc.docstatus<1)
//   //       // {
//   //       //     frm.clear_table("locations");
//   //       //     frm.refresh_fields();
//   //       //     return null
//   //       // };
//   //  }
    
// });

// frappe.ui.form.on("Pick List Item", {

// 	qty:function(frm,cdt,cdn){

// 		//console.log('Hi')
// 			let row = locals[cdt][cdn];
// 			//let row_item_code = row.item_code;
// 			//let row_qty = row.qty;
// 				// console.log(row.item_code);
// 				// console.log(row.qty);
// 					frappe.call({
// 						 method: 'frappe.client.get_value',
// 					    args: {
// 					        'doctype': 'Item',
// 					        'filters': {'name': row.item_code},
// 					        'fieldname': [
// 					         		'no_of_items_can_be_packed'
// 					        ]
// 					    },

// 					    callback: function(r) {
// 					        if (!r.exc) {
// 					            let packed_items = r.message.no_of_items_can_be_packed;
// 					            let remaining_qty = row.qty - packed_items;
// 					            //console.log(r.message.qty)
// 					            //console.log(row.qty);
// 					           // console.log(r.message);
// 					           	//r.message.qty = packed_items;
// 					           	 //frappe.model.set_value("Pick List", frm.doc, r.message.qty, packed_items)
// 					           	 //row.qty = packed_items; 

// 					           	 for (let i in row){
// 					           	 	console.log(i);
// 					           	 	if (row.qty > packed_items){
// 										let d = frm.add_child("locations");
// 										console.log(i.item_code);
// 										d.item_code = i.item_code
// 										d.description = i.description
// 										d.item_name = i.item_name
// 										d.item_group = i.item_group
// 										//d.warehouse = row.warehouse
// 										d.qty = remaining_qty
// 										d.stock_qty = remaining_qty
// 										d.picked_qty = remaining_qty
// 										d.no_of_items_can_be_packed = packed_items
// 										d.uom = i.uom
// 										d.conversion_factor = i.conversion_factor
// 										d.stock_uom = i.stock_uom 
// 										//d.carton_no = row.carton_qty + '-' + remaining_qty
// 										d.carton_qty = 0

// 					 				};
// 					           	 }
					           	 
// 					        }
// 					    }
// 					});

// 				frm.refresh_fields("locations");
// 		//});
// 	}

// });

frappe.ui.form.on("Pick List", {

    refresh:function(frm) {
        cur_frm.add_custom_button(__('Check & Update entries'), function() {           
                check_set(frm)
            });

    },
   get_item_locations: function(frm) {
        $.each(frm.doc.locations, function(i,v) {
                frappe.call({
                    method: 'frappe.client.get_value',
                    args: {
                        'doctype': 'Item',
                        'filters': {'name': v.item_code},
                        'fieldname': [
                            'no_of_items_can_be_packed'
                        ]
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.model.set_value(v.doctype, v.name, "no_of_items_can_be_packed",r.message.no_of_items_can_be_packed);                                    
                            
                            // frappe.model.set_value(v.doctype, v.name, "qty",v.no_of_items_can_be_packed);                                    
                            
                        }
                    }
                });
        });
        
   }
   // before_save: function(frm){
   //  frm.trigger('get_item_locations')
   // }
    
});

function check_set(frm) {
        $.each(frm.doc.locations, function(i,v) {
            var entered_qty = v.qty
            var loops = Math.floor(entered_qty/v.no_of_items_can_be_packed)
            console.log(loops);
            var pending_qty = Math.abs(entered_qty-(v.no_of_items_can_be_packed*loops))
            console.log(pending_qty);
            var remaining_qty = Math.abs(v.no_of_items_can_be_packed - entered_qty)

            if (v.no_of_items_can_be_packed < entered_qty ){
                frappe.model.set_value(v.doctype, v.name, "picked_qty",v.no_of_items_can_be_packed*loops);
                frappe.model.set_value(v.doctype, v.name, "qty",v.no_of_items_can_be_packed*loops);
                // while(loops-1 > 0) {    
                                                    
                //     var childTable = frm.add_child("locations");
                //     childTable.item_code= v.item_code
                //     childTable.qty = v.no_of_items_can_be_packed
                //     childTable.stock_qty = v.no_of_items_can_be_packed
                //     childTable.picked_qty = v.no_of_items_can_be_packed
                //     loops = 0
                // }
                while(pending_qty>0) {
                    var childTable = frm.add_child("locations");
                    childTable.item_code= v.item_code
                    //childTable.carton_qty= v.item_code
                    childTable.qty = pending_qty
                    childTable.stock_qty = pending_qty
                    childTable.picked_qty = pending_qty
                    pending_qty = 0
                }
            }
            else if(entered_qty < v.no_of_items_can_be_packed){
                frappe.model.set_value(v.doctype, v.name, "picked_qty",v.no_of_items_can_be_packed*loops);
                frappe.model.set_value(v.doctype, v.name, "qty",v.no_of_items_can_be_packed*loops);
        
                while(remaining_qty>0) {
                    var childTable = frm.add_child("locations");
                    childTable.item_code= v.item_code
                    //childTable.carton_qty= v.item_code
                    childTable.qty = entered_qty
                    childTable.stock_qty = entered_qty
                    childTable.picked_qty = entered_qty
                    remaining_qty = 0
                }

            }
            frm.refresh_fields("locations");
        }); 
   }