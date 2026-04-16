from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError

class BulkCreateInvoice(models.TransientModel):
    _name = 'bulk.create.invoice'
    _description = 'Bulk Create Invoice'

    def bulk_create_invoice(self):
        active_ids = self._context.get('active_ids')
        medical_lab_obj = self.env['medical.lab']
        list_of_ids = []
        res = ''
        account_invoice_obj = self.env['account.move']
        patient_id_list = []
        lab_obj=medical_lab_obj.search([('id','in',active_ids)])
        for s in lab_obj:
            if s.is_invoiced == True:
                raise UserError(_("'%s' Is  Already Invoiced " % s.name))

            if s.patient_id.patient_id.id not in patient_id_list and patient_id_list:
                raise UserError(_('Different Patient Not Allowed!'))
            patient_id_list.append(s.patient_id.patient_id.id)

        name = ','.join([s.name for s in lab_obj])

        for active_id in active_ids:
            lab_req = medical_lab_obj.browse(active_id)

            sale_journals = self.env['account.journal'].search([('type', '=', 'sale')])
            if not res:
                invoice_vals = {
                    'name': self.env['ir.sequence'].next_by_code('medical_lab_test_inv_seq'),
                    'invoice_origin': name or '',
                    'department_id': lab_req.patient_id.department_id.id or False,
                    'patient_type_id': lab_req.patient_type_id.id or False,
                    'move_type': 'out_invoice',
                    'ref': False,
                    'journal_id': sale_journals and sale_journals[0].id or False,
                    'partner_id': lab_req.patient_id.patient_id.id or False,
                    'partner_shipping_id': lab_req.patient_id.patient_id.id,
                    'currency_id': lab_req.patient_id.patient_id.currency_id.id,
                    'invoice_payment_term_id': False,
                    'fiscal_position_id': lab_req.patient_id.patient_id.property_account_position_id.id,
                    'team_id': False,
                    'invoice_date': date.today(),
                }
                res = account_invoice_obj.create(invoice_vals)
            product = lab_req.test_id.service_product_id
            invoice_line_account_id = False
            if product.id:
                invoice_line_account_id = product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id or False
            if not invoice_line_account_id:
                inc_acc = self.env['product.category'].browse('property_account_income_categ_id')
            if not invoice_line_account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                    (product.name,))
            tax_ids = []
            taxes = product.taxes_id.filtered(
                lambda r: not product.company_id or r.company_id == product.company_id)
            tax_ids = taxes.ids

            invoice_line_vals = {
                'name': lab_req.test_id.service_product_id.name or '',
                'account_id': invoice_line_account_id,
                'price_unit': lab_req.test_id.service_product_id.lst_price,
                'product_uom_id': lab_req.test_id.service_product_id.uom_id.id,
                'quantity': 1,
                'product_id': lab_req.test_id.service_product_id.id,
            }
            res1 = res.write({'invoice_line_ids': ([(0, 0, invoice_line_vals)])})
            lab_req.write({'is_invoiced': True})
        list_of_ids.append(res.id)
        if list_of_ids:
            imd = self.env['ir.model.data']
            action = self.env.ref('account.action_move_out_invoice_type')
            list_view_id = imd._xmlid_to_res_id('account.view_invoice_tree')
            form_view_id = imd._xmlid_to_res_id('account.view_move_form')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'list'], [form_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,

            }
            if list_of_ids:
                result['domain'] = "[('id','=',%s)]" % list_of_ids

            return result

