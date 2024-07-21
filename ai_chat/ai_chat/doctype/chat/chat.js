// Copyright (c) 2024, jibreel abdeen and contributors
/// For license information, please see license.txt

frappe.ui.form.on("chat", {
	refresh(frm) {

	},
    ask: function(frm){
        frappe.call({
            method:"ai_chat.ai_chat.doctype.chat.chat.get_ai_answer",
            args:{
                "request":frm.doc.request,
            },
            callback: function(r){
                frm.set_value('response',  r.message);
            },
        });
    }
});
