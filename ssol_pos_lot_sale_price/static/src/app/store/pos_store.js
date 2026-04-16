/** @odoo-module **/

const { PosStore } = require('@point_of_sale/app/services/pos_store');
const { patch } = require('@web/core/utils/patch');
import {
    makeAwaitable,
    ask,
    makeActionAwaitable,
} from "@point_of_sale/app/utils/make_awaitable_dialog";
import { SelectLotPopup } from "@point_of_sale/app/components/popups/select_lot_popup/select_lot_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";



patch(PosStore.prototype, {
    async editLots(product, packLotLinesToEdit) {
        const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
        let canCreateLots =
            this.pickingType.use_create_lots || !this.pickingType.use_existing_lots;

        let existingLots = [];
        try {
            existingLots = await this.data.call("pos.order.line", "get_existing_lots", [
                this.company.id,
                this.config.id,
                product.id,
            ]);

            if (!canCreateLots && (!existingLots || existingLots.length === 0)) {
                this.dialog.add(AlertDialog, {
                    title: _t("No existing serial/lot number"),
                    body: _t(
                        "There is no serial/lot number for the selected product, and their creation is not allowed from the Point of Sale app."
                    ),
                });
                return null;
            }
        } catch (ex) {
            console.error("Collecting existing lots failed: ", ex);

            const confirmed = await ask(this.dialog, {
                title: _t("Server communication problem"),
                body: _t(
                    "The existing serial/lot numbers could not be retrieved. \nContinue without checking the validity of serial/lot numbers ?"
                ),
                confirmLabel: _t("Yes"),
                cancelLabel: _t("No"),
            });

            if (!confirmed) {
                return null;
            }
            canCreateLots = true;
        }

        // 🔥 NEW: Filter only lots موجود in POS + qty > 0
        const existingLotsName = existingLots.map((l) => l.name);

        const validLots = this.models["stock.lot"].filter(
            (lot) =>
                existingLotsName.includes(lot.name) &&
                lot.product_qty > 0
        );

        const validLotsName = validLots.map((lot) => lot.name);

        // Replace existingLots with filtered ones
        existingLots = existingLots.filter((lot) =>
            validLotsName.includes(lot.name)
        );

        // 🔽 Odoo 19 ka original logic (UNCHANGED)
        const usedLotsQty = this.models["pos.pack.operation.lot"]
            .filter(
                (lot) =>
                    lot.pos_order_line_id?.product_id?.id === product.id &&
                    lot.pos_order_line_id?.order_id?.state === "draft"
            )
            .reduce((acc, lot) => {
                if (!acc[lot.lot_name]) {
                    acc[lot.lot_name] = { total: 0, currentOrderCount: 0 };
                }
                acc[lot.lot_name].total += lot.pos_order_line_id?.qty || 0;

                if (lot.pos_order_line_id?.order_id?.id === this.selectedOrder.id) {
                    acc[lot.lot_name].currentOrderCount +=
                        lot.pos_order_line_id?.qty || 0;
                }
                return acc;
            }, {});

        // Remove already fully used lots
        existingLots = existingLots.filter(
            (lot) => lot.product_qty > (usedLotsQty[lot.name]?.total || 0)
        );

        const isLotNameUsed = (itemValue) => {
            const totalQty =
                existingLots.find((lt) => lt.name == itemValue)?.product_qty || 0;

            const usedQty = usedLotsQty[itemValue]
                ? usedLotsQty[itemValue].total -
                  usedLotsQty[itemValue].currentOrderCount
                : 0;

            return usedQty ? usedQty >= totalQty : false;
        };

        const finalLotNames = existingLots.map((l) => l.name);

        if (!packLotLinesToEdit.length && finalLotNames.length === 1) {
            return { newPackLotLines: [{ lot_name: finalLotNames[0] }] };
        }

        const payload = await makeAwaitable(this.dialog, SelectLotPopup, {
            title: _t("Lot/Serial number(s) required for"),
            name: product.display_name,
            isSingleItem: isAllowOnlyOneLot,
            array: packLotLinesToEdit,
            options: existingLots,
            customInput: canCreateLots,
            uniqueValues: product.tracking === "serial",
            isLotNameUsed: isLotNameUsed,
        });

        if (payload) {
            const modifiedPackLotLines = Object.fromEntries(
                payload
                    .filter((item) => item.id)
                    .map((item) => [item.id, item.text])
            );

            const newPackLotLines = payload
                .filter((item) => !item.id)
                .map((item) => ({ lot_name: item.text }));

            return { modifiedPackLotLines, newPackLotLines };
        } else {
            return null;
        }
    },
});