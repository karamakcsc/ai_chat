// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Commonly Known", {
    submit: function(frm) {
        frappe.call({
            method: "ai_chat.ai_chat.doctype.item_commonly_known.item_commonly_known.generate_response",
            args: {
                "cid": frm.docname,
                "token": frappe.session.user,
                "dynamic_doc": frm.doc.dynamic_doc,
            },
            freeze: true,
            freeze_message: 'Please wait...',
            callback: function(r) {
                frm.set_value('commonly_known', r.message);
            }
        });
    },
});

frappe.ui.form.on("Item Commonly Known", {
    setup: function(frm) {
		frm.set_query("dynamic_doc", function() {
			return {
				filters: {
					"has_variants" : 0,
                }
			}
		});
	}
});

// cur_frm.fields_dict.document.get_query = function(doc,cdt,cdn) {
//     return {
//         filters:[
//             ['has_variant', '=', 0]
//         ]
//     }
// }

// frappe.ui.form.on('Item Commonly Known', {
//     setup(frm) {
//             cur_frm.fields_dict.document.get_query = function(doc) {
//                  return {
//                      filters: {
//                          "has_variant": 0
//                      }
//                  };
//             };
//     },
// });