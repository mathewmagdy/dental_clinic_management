from odoo import api,fields, models,_
from odoo.exceptions import ValidationError


class department(models.Model):
    _name="dental.department"
    _description="services info"
    
    
    department_name=fields.Char("Department name", required=True,tracking=True)
    ref=fields.Char(string="Department_reference",default=lambda self:_('New Depatment'))
    
    
    @api.model_create_multi      
    def create(self,value_list):
        for val in value_list:
            val['ref'] = self.env['ir.sequence'].next_by_code('dental.department')
        return super(department,self).create(value_list)
    
    def name_get(self):
        res=[]
        for rec in self:
            new_name=f'{rec.ref}-{rec.department_name}'
            res.append((rec.id,new_name))
        return res
    
   