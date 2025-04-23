from odoo import api,fields, models,_
from odoo.exceptions import ValidationError

class DentalServices(models.Model):
    _name="dental.services"
    _description="services info"
    
    
    service_name=fields.Char("service name", required=True,tracking=True)
    ref=fields.Char(string="Service_reference",default=lambda self:_('New service'))
    department_id=fields.Many2one('dental.department' ,string="Depatrment")
    price=fields.Integer("Service Price",required=True,traking=True)
   
    @api.model_create_multi      
    def create(self,value_list):
        for val in value_list:
            val['ref'] = self.env['ir.sequence'].next_by_code('dental.services')
        return super(DentalServices,self).create(value_list)
    