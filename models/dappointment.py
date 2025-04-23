from odoo import models, fields, api,_
import urllib.parse
from odoo.exceptions import ValidationError


class Appointment(models.Model):
    _name = 'dental.dappointment'
    _description = 'Appointment'
    _inherit="mail.thread"

    ref=fields.Char(string="Appointment Reference",default=lambda self:_('New Appointment'))
    patient_id=fields.Many2one("dental.patient",string="Patient")
    appointment_date= fields.Datetime(string='Appointment Date', required=True)
    phone_number = fields.Char(string='Phone', related='patient_id.phone', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Note')
    search_state = fields.Selection(
        [('all', 'all'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'),('done', 'Done')],
        string='Search Status',
        default='all'
    )


    @api.onchange(state)
    def action_confirm(self):
        for appointment in self:
            appointment.state = 'confirmed'

    @api.onchange(state)
    def action_cancel(self):
        for appointment in self:
            appointment.state = 'cancelled'
            
    @api.onchange(state)
    def action_done(self):
        for appointment in self:
            appointment.state = 'done'
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code("dental.dappointment")
        return super(Appointment,self).create(vals_list)   
    
    @api.onchange('appointment_date')
    def _check_appointment_availability(self):
        if self.appointment_date:
            domain = [
                ('appointment_date', '=', self.appointment_date),
                ('state', 'in', ['confirmed', 'draft']),  # Check for existing appointments
            ]
            existing_appointments = self.search(domain)
            if existing_appointments:
                return {
                    'warning': {
                        'title': 'Warning',
                        'message': 'This appointment time is already booked.'
                    }
                }
    def action_create_exam(self):
        self.ensure_one()
        exam_vals = {
            'patient_id': self.patient_id.id,
            'date':self.appointment_date
        }

        try:
            # Attempt to convert exam_id to a number (assuming it's an ID)
            exam_id = int(self.env['dental.exam'].create(exam_vals))
        except ValueError:
            # Handle the case where conversion fails (e.g., non-numeric ID)
            print("Error: exam_id cannot be converted to a number.")
            return {
                # Handle the error, such as displaying a message to the user
            }

        return {
            'type': 'ir.actions.act_window',
            'name': _('Examination'),
            'res_model': 'dental.exam',
            'res_id': exam_id,
            'view_mode': 'form',
            'target': 'current',
        }
    def send_whatsapp_msg(self):
        if not self.phone_number:
            raise ValidationError(_('Missing phone number!'))
    
    # Prepare the message
        message = f"Hi Mr.{self.patient_id.name} your appointment date is {self.appointment_date}"
    
    # URL encode the message to handle special characters like spaces, punctuation, etc.
        encoded_message = urllib.parse.quote(message)
    
    # Create the WhatsApp link
        whats_link_api = "https://web.whatsapp.com/send?phone=%s&text=%s" % (self.phone_number, encoded_message)
    
    # Return the action to open the WhatsApp link
        return {
        'type': 'ir.actions.act_url',
        'target': 'new',
        'url': whats_link_api
    }
    