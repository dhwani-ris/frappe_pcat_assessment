frappe.ui.form.on('LMS Question', {
    refresh: function(frm) {
        // Trigger the type change handler on form refresh if type is already set to PCAT
        if (frm.doc.type === 'PCAT') {
            prefill_pcat_options(frm);
        }
    },
    
    type: function(frm) {
        if (frm.doc.type === 'PCAT') {
            prefill_pcat_options(frm);
        } else {
            // Clear options if type is changed from PCAT to something else
            clear_options(frm);
        }
    }
});

function prefill_pcat_options(frm) {
    // Fetch RIASEC Answer Options and prefill the option fields
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'RIASEC Answer Options',
            fields: ['option', 'value'],
            order_by: 'creation asc',
            limit_page_length: 4
        },
        callback: function(response) {
            if (response.message && response.message.length > 0) {
                const options = response.message;
                
                // Prefill options based on available data from database
                for (let i = 0; i < Math.min(options.length, 4); i++) {
                    const option_field = `option_${i + 1}`;
                    const option_text = `${options[i].option}`;
                    
                    frm.set_value(option_field, option_text);

                    // Set first option as correct by default
                    if (i === 0) {
                        frm.set_value(`is_correct_${i + 1}`, 1);
                    } else {
                        frm.set_value(`is_correct_${i + 1}`, 0);
                    }
                }
                
                frm.refresh_fields();
            } else {
                frappe.show_alert({
                    message: __('No RIASEC Answer Options found in database'),
                    indicator: 'orange'
                });
            }
        },
        error: function() {
            frappe.show_alert({
                message: __('Error fetching RIASEC Answer Options'),
                indicator: 'red'
            });
        }
    });
}



function clear_options(frm) {
    // Clear all option fields when type is changed from PCAT
    for (let i = 1; i <= 4; i++) {
        frm.set_value(`option_${i}`, '');
        frm.set_value(`is_correct_${i}`, 0);
        frm.set_value(`explanation_${i}`, '');
    }
    frm.refresh_fields();
}
