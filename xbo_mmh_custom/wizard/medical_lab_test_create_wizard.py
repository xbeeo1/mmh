# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class medical_lab_test_create(models.TransientModel):
    _inherit = 'medical.lab.test.create'
    _description = 'medical lab test create'

    def create_lab_test(self):
        res_ids = []
        lab_rqu_obj = self.env['medical.patient.lab.test']
        browse_records = lab_rqu_obj.browse(self._context.get('active_ids'))
        result = {}
        if not browse_records.outsourced_lab_request:
            for browse_record in browse_records:
                medical_lab_obj = self.env['medical.lab']
                for line in browse_record.lab_test_lines:

                    res = medical_lab_obj.create({'name': self.env['ir.sequence'].next_by_code('ltest_seq'),
                                                  'patient_id': browse_record.patient_id.id or False,
                                                  'date_requested': browse_record.date or False,
                                                  'test_id': line.medical_test_type_id.id or False,
                                                  'requestor_physician_id': browse_record.doctor_id.id or False,
                                                  })
                    critearea_lines = [(5, 0, 0)]
                    for cri in line.medical_test_type_id.critearea_ids:
                        critearea_line_vals = {
                            'seq': cri.seq or '',
                            'name': cri.name or '',
                            'normal_range': cri.normal_range,
                            'lab_test_unit_id': cri.lab_test_unit_id.id,
                        }
                        critearea_lines.append((0, 0, critearea_line_vals))

                    res1 = res.write({'critearea_ids': critearea_lines})
                    res_ids.append(res.id)
                if res_ids:
                    imd = self.env['ir.model.data']
                    write_ids = lab_rqu_obj.browse(self._context.get('active_id'))
                    write_ids.write({'state': 'tested'})
                    action = self.env.ref('basic_hms.action_medical_lab_tree')
                    list_view_id = imd._xmlid_to_res_id('basic_hms.medical_lab_tree_view')
                    form_view_id = imd._xmlid_to_res_id('basic_hms.medical_lab_form_view')
                    result = {
                        'name': action.name,
                        'help': action.help,
                        'type': action.type,
                        'views': [[list_view_id, 'list'], [form_view_id, 'form']],
                        'target': action.target,
                        'context': action.context,
                        'res_model': action.res_model,
                        'res_id': res.id,

                    }
                if res_ids:
                    result['domain'] = "[('id','in',%s)]" % res_ids
        else:
            for browse_record in browse_records:
                medical_lab_obj = self.env['outsourced.lab.request']
                res = medical_lab_obj.create({'name': self.env['ir.sequence'].next_by_code('olrtest_seq'),
                                              'patient_id': browse_record.patient_id.id or False,
                                              'date_requested': browse_record.date or False,
                                              'requestor_physician_id': browse_record.doctor_id.id or False,
                                              'partner_lab_id': browse_record.partner_lab_id.id or False,
                                              })
                critearea_lines = [(5, 0, 0)]
                for line in browse_record.lab_test_lines:
                    critearea_line_vals = {
                        'medical_test_type_id': line.medical_test_type_id.id,
                    }
                    critearea_lines.append((0, 0, critearea_line_vals))

                res1 = res.write({'outsourced_lab_test_lines': critearea_lines})
                res_ids.append(res.id)
            if res_ids:
                imd = self.env['ir.model.data']
                write_ids = lab_rqu_obj.browse(self._context.get('active_id'))
                write_ids.write({'state': 'tested'})
                action = self.env.ref('xbo_mmh_custom.action_outsourced_lab_request')
                list_view_id = imd._xmlid_to_res_id('xbo_mmh_custom.outsourced_lab_request_tree_view')
                form_view_id = imd._xmlid_to_res_id('xbo_mmh_custom.outsourced_lab_request_form_view')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'list'], [form_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                    'res_id': res.id,

                }
            if res_ids:
                result['domain'] = "[('id','in',%s)]" % res_ids

        return result