// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Migrate-Items-w-Pandas", {
    translate_text(frm) {
        frappe.call({
            doc: frm.doc,
            method: "translate_text",
            freeze: true,
            freeze_message: 'Translating text...',
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint(r.message);
                } else {
                    // frappe.msgprint('Translation failed or returned no message.');
                }
            }
        });
    }
});
