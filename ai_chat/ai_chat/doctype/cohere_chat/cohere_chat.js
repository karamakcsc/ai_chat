// Copyright (c) 2024, jibreel abdeen and contributors
// For license information, please see license.txt


var history_new;

frappe.ui.form.on("cohere_chat", {
	// refresh(frm) {
    //     console.clear();
    //     history_new = "";
    //     frappe.call({
    //         method:"ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.clear_chat",
    //         args:{
    //             "cid":frm.docname, 
    //             "token":frappe.session.user, 
    //         },
    //         callback: function(r){
    //             frm.set_value('history',  r.message[0]);
    //             frm.set_value('user_message',  r.message[1]);
    //             console.log(r.message[2]);
    //         },
    //     });
	// },
    submit: function(frm){
        // alert(frappe.session.sid);
        // frappe.msgprint(frappe.session.sid , frappe.session.user );
        // frappe.msgprint("This is a message"+  frm.docname );
        frappe.call({
            method:"ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.generate_response",
            args:{
                "user_message":frm.doc.user_message,
                "cid":frm.docname, 
                "token":frappe.session.user, 
            },
            freeze: true,
            freeze_message: 'Please wait...',
            callback: function(r){
                last_reply = r.message[1][1].slice(-2);
                // history_new += frappe.session.user + ": " + last_reply[0] + "\n" + "Cohere_Ai: " + last_reply[1] + "\n";
                // frm.set_value('history', history_new);
                // frm.set_value('user_message',  "");
                frappe.call({
                    method:"ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.get_json_text",
                    args:{
                        "message":last_reply[1] ,
                    },
                    callback: function(r){
                        frm.set_value('history', r.message);
                        // frm.set_value('user_message',  "");
                    },
                });
                // frappe.call({
                //     method:"ai_chat.ai_chat.doctype.jsontexttojson.jsontexttojson.generate_response",
                //     args:{
                //         "message":last_reply[1] ,
                //     },
                //     callback: function(r){
                //         console.log(r.message);
                //     },
                // });
            }
        });
    },
    clear: function(frm){
        // alert(frappe.session.sid);
        console.clear();
        history_new = "";
        frappe.call({
            method:"ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.clear_chat",
            args:{
                "cid":frm.docname, 
                "token":frappe.session.user, 
            },
            callback: function(r){
                frm.set_value('history',  r.message[0]);
                frm.set_value('user_message',  r.message[1]);
                console.log(r.message[2]);
            },
        });
    },
    // check_items_availability: function(frm) {
        
    //     frappe.call({
    //         doc: frm.doc,
    //         method: "ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.items_availability_check",
    //         args: {
    //             json_text: frm.doc.history
    //         },
    //         callback: function(r) {
    //             frappe.msgprint(r.message);
    //             frm.refresh_field('available_items_and_qty');
    //             frm.refresh_field('unavailable_qty');
    //             frm.refresh_field('unavailable_item');
    //         }
    //     });
    // }
});

// frappe.ui.form.on("cohere_chat", {
//     // refresh: function(frm) {
//     //     frm.events.check_items_availability(frm);
//     // },

//     check_items_availability: function(frm) {
//         frappe.call({
//             method: "ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.items_availability_check",
//             args: {
//                 json_text: frm.doc.history,
//                 name: frm.doc.name,
//             },
//             callback: function(r) {
//                 frappe.msgprint(r.message);
//                 frm.refresh_fields();
//             }
//         });
//     },
//     refresh_fields: function(frm) {
//         // frm.refresh_field("available_items_and_qty");
//         // frm.refresh_field("unavailable_qty");
//         // frm.refresh_field("unavailable_item");
//         frm.refresh_fields();
//     }
// });
// frappe.ui.form.on('cohere_chat', {
//     refresh: function(frm) {
        // frm.refresh_field("available_items_and_qty");
        // frm.refresh_field("unavailable_qty");
        // frm.refresh_field("unavailable_item");
//     }
// });
// frappe.ui.form.on("cohere_chat", {
//     validate: function(frm) {
//         frappe.call({
//             doc: frm.doc,
//             method: "ai_chat.api.create_purchase_order",
//             args: {
//                 company: frm.doc.company,
//                 supplier: frm.doc.supplier,
//                 ai_json: frm.doc.history
//             },
//             callback: function(r){
//                 console.log("Purchase Order Complete")
//             },
//         });
//     },
// });
frappe.ui.form.on("cohere_chat", {
    on_submit: function(frm) {
        frappe.call({
            method: "ai_chat.api.create_purchase_order",
            args: {
                company: frm.doc.company,
                supplier: frm.doc.supplier,
                ai_json: frm.doc.history
            },
            callback: function(r) {
                if (r.message) {
                    console.log("Purchase Order Complete:", r.message);
                } else {
                    console.log("Purchase Order creation failed or returned no message");
                }
            },
        });
    },
});

frappe.ui.form.on("cohere_chat", {
    cohere_message: function(frm) {
        frappe.call({
            method: "ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.analyze_child_table_data",
            args: {
                docname: frm.docname,
                token: frappe.session.user,
            },
            freeze: true,
            freeze_message: 'Analyzing data...',
            callback: function(r) {
                if (r.message) {
                    frm.set_value('cohere_message_for_user', r.message);
                } else {
                    frappe.msgprint("Analysis failed or returned no message.");
                }
            }
        });
    },
});

// frappe.ui.form.on("cohere_chat", {
//     check_item_description: function(frm) {
//         frappe.call({
//             method: "ai_chat.ai_chat.doctype.cohere_chat.cohere_chat.check_item_description",
//             callback: function(r) {
//                 if (r.message) {
//                     frappe.msgprint(r.message);
//                 } else {
//                     frappe.msgprint("Analysis failed or returned no message.");
//                 }
//             }
//         });
//     },
// });