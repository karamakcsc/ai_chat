// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Generate Items Description", {
	check_items_description: function(frm) {
                frappe.call({
                    doc: frm.doc,
                    method: "check_item_description",
                    freeze: true,
                    freeze_message: 'Wait...',
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                        }
                    }
                });
            },
});

frappe.ui.form.on("Generate Items Description", {
	before_submit: function(frm) {
                frappe.call({
                    doc: frm.doc,
                    method: "submit_item_description",
                    freeze: true,
                    freeze_message: 'Wait...',
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                        }
                    }
                });
            },
});

// frappe.ui.form.on("Generate Items Description", {
// 	setup: function(frm) {
//                 frappe.call({
//                     doc: frm.doc,
//                     method: "count_items",
//                     // callback: function(r) {
//                     //     if (r.message) {
//                     //         frappe.msgprint(r.message);
//                     //     }
//                     // }
//                 });
//             },
// });