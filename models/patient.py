from odoo import api,fields, models,_
from odoo.exceptions import ValidationError
import urllib.parse


class patient(models.Model):
    _name="dental.patient"
    _description="Patient info"
    _inherit="mail.thread"
    
    name=fields.Char(string="Name",required=True)
    age=fields.Integer(string="Age",compute="Calculate_Age",store=True)
    is_chield=fields.Boolean(string="Is chield?!")
    notes=fields.Text(string="Notes")
    phone=fields.Char(string="Phone",required=True)
    gender=fields.Selection([('male',"Male"),('female','Female')],string="Gender")
    date_of_birth=fields.Date(string="Date_Of_Birth")
    ref=fields.Char(string="Reference",default=lambda self:_("new"))
    # this questions used in medical history
    q1=fields.Boolean(string="Are you currently pregnant or breastfeeding?")
    q2=fields.Boolean(string="Do you have any heart conditions?")
    q3=fields.Boolean(string="Do you have any respiratory conditions?")
    q4=fields.Boolean(string="Do you have diabetes?")
    q5=fields.Boolean(string="Are you currently taking any medications?")
    q6=fields.Boolean(string="Do you have any cavities or fillings?")
    q7=fields.Boolean(string="Do you have any gum disease?")
    q8=fields.Boolean(string="Do you have any difficulty opening your mouth?")
    
    
    #functions
    @api.onchange('age')  
    def _on_change_age(self):
        if self.age<=15:
            self.is_chield=True
        else:
            self.is_chield=False 
   
    
    @api.constrains('is_chield','age')
    def check_chield_age(self):
        for rec in self:
            if rec.is_chield and rec.age <=0:
                raise ValidationError(_('Age not valid'))
            
    
    @api.depends('date_of_birth')
    def Calculate_Age(self):
        for rec in self:
            if rec.date_of_birth:
                today = fields.Date.today()
                age = today.year - rec.date_of_birth.year - ((today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day))
                rec.age = age
            else:
                rec.age = 0
                
                
    #inhirit form exist class            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref'] = self.env['ir.sequence'].next_by_code("dental.patient")

        return super(patient,self).create(vals_list)
    
    def action_share_whatsapp(self):
        if not self.phone:
            raise ValidationError(_('Missing phone number!'))
    
    # Prepare the message
        message = 'Hi Mr. ' + self.name
    
    # URL encode the message to handle special characters like spaces, punctuation, etc.
        encoded_message = urllib.parse.quote(message)
    
    # Create the WhatsApp link
        whats_link_api = "https://web.whatsapp.com/send?phone=%s&text=%s" % (self.phone, encoded_message)
    
    # Return the action to open the WhatsApp link
        return {
        'type': 'ir.actions.act_url',
        'target': 'new',
        'url': whats_link_api
    }