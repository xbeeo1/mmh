/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {

    /**
     * Override pack lot display for refund case
     */
    get packLotLines() {
        if (this.refunded_orderline_id) {
            const originalLots = this.refunded_orderline_id.pack_lot_ids || [];

            return originalLots.map((lot) => {
                const trackingType = this.product_id.tracking;
                return `${trackingType === "lot" ? "Lot Number" : "SN"} ${lot.lot_name}`;
            });
        }

        // fallback to original behavior
        return this.pack_lot_ids.map(
            (l) =>
                `${l.pos_order_line_id.product_id.tracking == "lot" ? "Lot Number" : "SN"} ${
                    l.lot_name
                }`
        );
    },

    /**
     * Get lot-based price if exists
     */
    getPriceWithLotFallback() {
        if (this.pack_lot_ids?.length) {
            const lot_name = this.pack_lot_ids[0]?.lot_name;
            console.log('111lot_name111',lot_name)
            const lot_obj = this.models["stock.lot"].find(
                (p) => p.name === lot_name
            );
            console.log('111lot_obj111',lot_obj)
            if (lot_obj?.sale_price) {
                return lot_obj.sale_price;
            }
        }
        return false;
    },

    /**
     * Override Odoo 19 method
     */
    setUnitPrice(price) {
        let parsed_price =
            typeof price === "number"
                ? price
                : isNaN(parseFloat(price))
                ? 0
                : parseFloat("" + price);

        const lot_price = this.getPriceWithLotFallback();

        if (lot_price && this.price_type !== "manual") {
            parsed_price = lot_price;
        }

        const ProductPrice = this.models["decimal.precision"].find(
            (dp) => dp.name === "Product Price"
        );

        this.price_unit = ProductPrice.round(parsed_price || 0);
    },
});