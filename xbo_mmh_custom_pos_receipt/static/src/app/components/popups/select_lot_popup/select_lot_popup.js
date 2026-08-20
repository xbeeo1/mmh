/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { SelectLotPopup } from "@point_of_sale/app/components/popups/select_lot_popup/select_lot_popup";

patch(SelectLotPopup.prototype, {
    getSources() {
        return [
            {
                options: (currentInput) => {
                    const filteredOptions = this.props.options.filter(
                        (option) =>
                            option.name
                                .toLowerCase()
                                .includes(currentInput.toLowerCase()) &&
                            !this.state.values.some(
                                (value) => value.text === option.name
                            )
                    );

                    if (filteredOptions.length) {
                        return filteredOptions.map((option) => {
                            const qty = option.product_qty ?? 0;
                            const expiration = option.expiration_date || "N/A";

                            return {
                                label: `${option.name} | Qty: ${qty} | Exp: ${expiration}`,

                                onSelect: () =>
                                    this.onSelect({
                                        create: true,
                                        id: option.id,
                                        label: option.name,
                                    }),
                            };
                        });
                    }

                    if (this.props.customInput && currentInput) {
                        const label = _t(
                            "Create Lot/Serial number..."
                        );

                        return [
                            {
                                label,

                                onSelect: () =>
                                    this.onSelect({
                                        create: true,
                                        currentInput,
                                        id: currentInput,
                                        label,
                                    }),
                            },
                        ];
                    }

                    return [
                        {
                            label: _t(
                                "No existing Lot/Serial number found..."
                            ),

                            onSelect: () =>
                                this.onSelect({
                                    create: false,
                                }),
                        },
                    ];
                },
            },
        ];
    },
});