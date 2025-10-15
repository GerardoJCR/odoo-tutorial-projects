from odoo import fields, models

class ResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        comodel_name = 'estate.property',
        inverse_name = 'seller_id', #campo que apunta  al vendedor  en estate.property
        string = 'Propiedades',
        domain = [('state', '=', 'new')] #solo mostrara propiedades disponibles
        
    )

    
