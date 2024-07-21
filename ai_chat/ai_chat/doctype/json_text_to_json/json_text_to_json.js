// Copyright (c) 2024, jibreel abdeen and contributors
// For license information, please see license.txt

// frappe.ui.form.on("jsontexttojson", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("jsontexttojson", {
	refresh(frm) {
        console.clear();
        frappe.call({
            method:"ai_chat.ai_chat.doctype.jsontexttojson.jsontexttojson.clear_chat",
            args:{
            },
            callback: function(r){
                frm.set_value('json_text',  r.message[0]);
                frm.set_value('json',  r.message[1]);
                console.log(r.message[2]);
            },
        });
	},
    go: function(frm){
        // alert(frappe.session.sid);
        // frappe.msgprint(frappe.session.sid , frappe.session.user );
        // frappe.msgprint("This is a message"+  frm.docname );
        frappe.call({
            method:"ai_chat.ai_chat.doctype.jsontexttojson.jsontexttojson.generate_response",
            args:{
                "message":frm.doc.json_text,
            },
            callback: function(r){
                frm.set_value('json',  r.message);
                // parse json text to json object  
                console.log(r.message);
            },
        });
    },
});    