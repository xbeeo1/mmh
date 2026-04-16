/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ResPartner } from "@point_of_sale/app/models/res_partner";


// Patch ResPartner model to include the patient_type_id field for POS
patch(ResPartner, {
    fields: {
        ...ResPartner.fields,
        patient_type_id: {
            type: "many2one",
            relation: "patient.type",
        },
    },
});


