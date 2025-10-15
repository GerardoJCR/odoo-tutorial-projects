from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name ="estate.property.type"
    _description = "Tipo de Propiedad Inmobiliaria"
    _order = "name"
    
    name = fields.Char(default="House", required=True)
    sequence = fields.Integer(string="Secuencia", default=10, help="Usalo para ordenar manualmente")
    property_ids = fields.One2many(comodel_name="estate.property", inverse_name="property_type_id" ,string="Propiedades") 
    
    offer_ids = fields.One2many(comodel_name="estate.property.offer" ,inverse_name="property_type_id", string="Offers"
    )
    offer_count = fields.Integer(
        string="Offer Count",
        compute="_compute_offer_count"
    )
    
    # @api.depends('offer_ids')
    # def _compute_offer_count(self):
    #     for record in self:
    #         if record.offer_ids:
    #             record.offer_count = len(record.offer_ids)
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids) if record.offer_ids else 0


    _sql_constraints = [
        (
            'unique_property_type_name',
            'UNIQUE(name)',
            'EL nombre del tipo de propiedad debe ser unico'
        )
    ]