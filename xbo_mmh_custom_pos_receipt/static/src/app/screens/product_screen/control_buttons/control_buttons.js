/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectionPopup } from "@point_of_sale/app/components/popups/selection_popup/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {
    async selectOrderType() {
        const order = this.pos.getOrder();

        const typeList = [
            {
                id: "ward",
                label: _t("Ward"),
                isSelected: order.order_type === "Ward",
                item: "Ward",
            },
            {
                id: "ot",
                label: _t("OT"),
                isSelected: order.order_type === "OT",
                item: "OT",
            },
        ];

        const selectedType = await makeAwaitable(
            this.dialog,
            SelectionPopup,
            {
                title: _t("Select Type"),
                list: typeList,
            }
        );

        if (selectedType) {
            order.order_type = selectedType;
        }
    },
});