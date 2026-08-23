# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Syamili K (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPickingInherit(models.Model):
    """This class inherits 'stock.picking' and adds required fields """
    _inherit = 'stock.picking'

    auto_generated = fields.Boolean(string='Auto Generated Transfer',
                                    copy=False,
                                    help="Field helps to check the picking is "
                                         "created from an another picking "
                                         "or not")
    is_backorder_button_clicked = fields.Boolean(default=False,
                                                 string='Backorder'
                                                        ' Button Clicked')

    def button_validate(self):
        # Configuration Validation
        for picking in self:
            account_config = self.env['stock.transfer.account'].search([
                ('company_id', '=', picking.company_id.id)
            ], limit=1)
            in_company_id = self.env['res.company'].sudo().search(
                [('partner_id', '=', self.partner_id.id)], limit=1)

            if not account_config and in_company_id:
                raise UserError(_(
                    "Please configure Stock Transfer Accounts for company '%s' before validating this transfer."
                ) % picking.company_id.name)

        # Validate Picking First
        result = super(StockPickingInherit, self).button_validate()

        # Existing Intercompany Logic
        active_move = []
        greater_quantity = []

        for move in self.move_ids:
            if move.quantity != 0.0:
                if move.quantity != move.product_uom_qty:
                    active_move.append(move.id)

            if move.quantity > move.product_uom_qty:
                greater_quantity.append(move.id)

        if len(greater_quantity) == self.move_ids.search_count([
            ('picking_id', '=', self.id)
        ]):
            if not self.auto_generated:
                self.create_intercompany_transfer()

        if not self.move_ids.search([
            ('picking_id', '=', self.id),
            ('quantity', '=', 0.0)
        ]):
            if not active_move:
                if not self.auto_generated:
                    self.create_intercompany_transfer()

        # Create Journal Entry After Successful Validation
        if account_config and in_company_id:
            for picking in self:
                account_config = self.env['stock.transfer.account'].search([
                    ('company_id', '=', picking.company_id.id)
                ], limit=1)

                misc_journal = self.env['account.journal'].search([
                    ('name', '=', 'Inter Branch Stock Transfer')
                ], limit=1)

                if not misc_journal:
                    raise UserError(_("Please configure 'Inter Branch Stock Transfer' journal."))

                lines = []

                for line in picking.move_ids:
                    amount = line.product_id.standard_price * line.quantity

                    lines.append((0, 0, {
                        'account_id': account_config.account_debit.id,
                        'debit': amount,
                        'credit': 0.0,
                        'name': picking.name,
                        'partner_id': picking.partner_id.id,
                    }))

                    lines.append((0, 0, {
                        'account_id': account_config.account_credit.id,
                        'debit': 0.0,
                        'credit': amount,
                        'name': picking.name,
                        'partner_id': picking.partner_id.id,
                    }))

                if lines:
                    move_obj = self.env['account.move'].create({
                        'ref': picking.name,
                        'journal_id': misc_journal.id,
                        'move_type': 'entry',
                        'line_ids': lines,
                    })
                    move_obj.action_post()

        return result

    def create_intercompany_transfer(self):
        """Create inter-company transfer with lot name,
        expiration date and exact transferred quantity.
        """

        self.ensure_one()

        # ---------------------------------------------------------
        # 1. Find destination company
        # ---------------------------------------------------------
        company_id = self.env['res.company'].sudo().search(
            [('partner_id', '=', self.partner_id.id)],
            limit=1
        )

        if not company_id:
            return

        # ---------------------------------------------------------
        # 2. Check inter-company transfer configuration
        # ---------------------------------------------------------
        if not company_id.enable_inter_company_transfer:
            return

        if not (
                self.picking_type_id.code == company_id.apply_transfer_type
                or company_id.apply_transfer_type == 'all'
        ):
            return

        # ---------------------------------------------------------
        # 3. Destination warehouse
        # ---------------------------------------------------------
        warehouse_ids = company_id.destination_warehouse_id.sudo()

        if not warehouse_ids:
            raise UserError(
                _('Please configure Destination Warehouse.')
            )

        # ---------------------------------------------------------
        # 4. Find destination operation type
        # ---------------------------------------------------------
        operation_type_id = False

        if self.picking_type_id.code == 'incoming':

            # Source is Incoming
            # Destination will be Outgoing
            operation_type_id = self.env[
                'stock.picking.type'
            ].sudo().search(
                [
                    ('warehouse_id', 'in', warehouse_ids.ids),
                    ('code', '=', 'outgoing'),
                ],
                limit=1
            )

        elif self.picking_type_id.code == 'outgoing':

            # Source is Outgoing
            # Destination will be Incoming
            operation_type_id = self.env[
                'stock.picking.type'
            ].sudo().search(
                [
                    ('warehouse_id', 'in', warehouse_ids.ids),
                    ('code', '=', 'incoming'),
                ],
                limit=1
            )

        else:
            raise UserError(
                _(
                    'Internal transfer between companies '
                    'are not allowed for this operation type.'
                )
            )

        if not operation_type_id:
            raise UserError(
                _(
                    'Please configure an appropriate operation type '
                    'for the destination company.'
                )
            )

        # ---------------------------------------------------------
        # 5. Get source and destination locations
        # ---------------------------------------------------------
        location_id = False
        location_dest_id = False

        if operation_type_id.default_location_src_id:
            location_id = operation_type_id.default_location_src_id.id

        elif self.company_id.partner_id:
            location_id = (
                self.partner_id.property_stock_supplier.id
            )

        if operation_type_id.default_location_dest_id:
            location_dest_id = (
                operation_type_id.default_location_dest_id.id
            )

        elif company_id.partner_id:
            location_dest_id = (
                company_id.partner_id.property_stock_customer.id
            )

        if not location_id or not location_dest_id:
            raise UserError(
                _(
                    'Please configure appropriate locations '
                    'on Operation Type or Partner.'
                )
            )

        # ---------------------------------------------------------
        # 6. Create destination picking
        # ---------------------------------------------------------
        picking_vals = {
            'partner_id': self.company_id.partner_id.id,
            'company_id': company_id.id,
            'picking_type_id': operation_type_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'auto_generated': True,
            'origin': self.name,
        }

        picking_id = self.env['stock.picking'].sudo().create(
            picking_vals
        )

        # ---------------------------------------------------------
        # 7. Create moves and move lines
        # ---------------------------------------------------------
        for move in self.move_ids:

            # Get only move lines belonging to this move
            source_move_lines = self.move_line_ids.filtered(
                lambda line: line.move_id == move
            )

            # -----------------------------------------------------
            # Calculate exact transferred quantity
            # -----------------------------------------------------
            done_qty = sum(
                source_move_lines.mapped('quantity')
            )

            # If there are no move lines / done quantity,
            # use original demanded quantity.
            if not done_qty:
                done_qty = move.product_uom_qty

            # -----------------------------------------------------
            # Create destination stock move
            # -----------------------------------------------------
            move_vals = {
                'picking_id': picking_id.id,
                'picking_type_id': operation_type_id.id,
                'product_id': move.product_id.id,
                'product_uom': move.product_uom.id,
                'product_uom_qty': done_qty,
                'location_id': location_id,
                'bypass_expiry_validation': True,
                'location_dest_id': location_dest_id,
                'company_id': company_id.id,
            }

            new_move = self.env['stock.move'].sudo().create(
                move_vals
            )

            # -----------------------------------------------------
            # 8. Copy source move lines
            # -----------------------------------------------------
            if source_move_lines:

                for source_line in source_move_lines:

                    line_qty = source_line.quantity

                    # Skip empty lines
                    if not line_qty:
                        continue

                    move_line_vals = {
                        'move_id': new_move.id,
                        'picking_id': picking_id.id,
                        'product_id': source_line.product_id.id,
                        'product_uom_id': source_line.product_uom_id.id,
                        'quantity': line_qty,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,

                        # Your custom field
                        'lot_name': source_line.lot_id.name,

                        # Your custom expiration field
                        'expiration_date': (
                            source_line.expiration_date
                        ),
                    }

                    self.env[
                        'stock.move.line'
                    ].sudo().create(move_line_vals)

            else:
                # -------------------------------------------------
                # If source has no move line, create one with
                # demanded quantity
                # -------------------------------------------------
                move_line_vals = {
                    'move_id': new_move.id,
                    'picking_id': picking_id.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'quantity': done_qty,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'lot_name': False,
                    'expiration_date': False,
                }

                self.env[
                    'stock.move.line'
                ].sudo().create(move_line_vals)

        # ---------------------------------------------------------
        # 9. Confirm destination picking
        # ---------------------------------------------------------
        if picking_id:
            picking_id.sudo().action_confirm()

            # Assign/reserve stock where applicable
            picking_id.sudo().action_assign()

        return picking_id