/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { useRef, onMounted } from "@odoo/owl";

// Patch the OrderReceipt component to inject custom HTML footer content into the receipt
patch(OrderReceipt.prototype, {
    setup() {
        super.setup();

        // Create OWL ref
        this.customFooterRef = useRef("custom_footer_area");

        // Inject HTML after DOM is mounted
        onMounted(() => {
            const el = this.customFooterRef.el;
            if (el && this.order.config.receipt_custom_footer) {
                el.innerHTML = this.order.config.receipt_custom_footer;
            }
        });
    },
});
