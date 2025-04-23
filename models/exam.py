from odoo import models, fields, api,_
from odoo.exceptions import UserError

class Exam(models.Model):
    _name = 'dental.exam'
    _description = 'Dental Exam'

    patient_id = fields.Many2one('dental.patient', string="Patient", required=True)
    date = fields.Datetime('Exam Date')
    notes = fields.Text('Notes')
    service = fields.Many2many('dental.services' , string="Services")
    total = fields.Integer(string="Total price" , compute="calculate_total" , store=True)

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            return {
                'domain': {
                    'patient_id': [('id', '=', self.patient_id)],
                },
            }
    
    @api.depends('service')
    def calculate_total(self):
        for record in self:
            # Assuming 'service' is a one-to-many field:
            record.total = sum(line.price for line in record.service)
    def action_create_invoice(self):
        if not self.patient_id:
            raise UserError("No appointment found for this exam.")

        invoice_vals = {
            'partner_id': 1,
            'invoice_date':self.date,
            'journal_id': 1, 
            'move_type': 'out_invoice'
        }

        invoice_lines = []
        for service in self.service:
            invoice_lines.append((0, 0, {
        'product_id': 1,
        'name': service.service_name,
        'quantity': 1,
        'price_unit': service.price,
        'account_id':1,
        'tax_ids':[]
        })) 
        invoice_vals['invoice_line_ids'] = invoice_lines
        invoice = self.env['account.move'].create(invoice_vals)
        return {
        'type': 'ir.actions.act_window',
        'name': 'invoice',
        'res_model': 'account.move',
        'view_mode': 'form',
        'res_id': invoice.id,
        'target': 'current',
        'context': {'default_type': 'out_invoice'}
    }