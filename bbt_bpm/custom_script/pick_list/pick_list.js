frappe.ui.form.on("Pick List", {

	   //var item = add_child_position(cur_frm.doc, "locations", "Pick List Item", 2)

	   //function add_child_position(doc,table_name,doctype,position){
    
    
    after_save:function(frm){
        // var SO = frm.doc.locations[0].sales_order    
        // console.log(frm.doc.locations[0].sales_order)
        // if (frm.doc.docstatus<1)
        // {
        //     frm.clear_table("locations");
        //     frm.refresh_fields();
        //     return null
        // };

        var grid_row = cur_frm.open_grid_row();
		grid_row.insert(true, true);
   }
    
});