from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class estatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"
    
    price = fields.Float(string="Precio")
    status = fields.Selection(
        selection=[
            ('pendient', 'Pendiente'),
            ('accepted', 'Aceptada'),
            ('refused', 'Rechazada'),
        ],
        string ="Status",
        copy=False,
        default="pendient"
    )

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True)

    property_id = fields.Many2one(comodel_name="estate.property", string="Property", required=True, ondelete='cascade')

    validity = fields.Integer(default= 7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline"
    )

    property_type_id = fields.Many2one(
    "estate.property.type",
    string="Property Type",
    related="property_id.property_type_id",
    store=True
)

    @api.depends('validity', 'create_date')
    def _compute_date_deadline(self):
        for record in self: 
            #Si no existe create_date. usamos today como base
            create_date = record.create_date or fields.Date.today()
            record.date_deadline = create_date + timedelta(days = record.validity)
    
    def _inverse_date_deadline(self):
        """Permite cambiar validity si el usuario cambia la fecha"""
        for record in self:
            create_date = record.create_date.date() or fields.Date.today()
            if record.date_deadline and create_date:
                delta = record.date_deadline - create_date
                record.validity = delta.days

    # @api.model
    # def create(self, valvs):
    #     offer = super().create(valvs)
    #     offer.property_id.state = "offer_received"
    #     return offer

    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])

        lista_precios = property.offer_ids.mapped('price')
        #Buscar la oferta mas alta
        max_price = max(lista_precios, default=0)
        if(vals['price'] <= max_price ):
            raise UserError(f"No puedes guardar una oferta menor o igual a la existente {max_price}")
        
        property.state = 'offer_received'

        return super().create(vals)


            





    def action_accept(self):
        for offer in self: 
            if offer.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'): 
                raise UserError("Ya hay una oferta aceptada para una propiedad")
            offer.status = "accepted"
            offer.property_id.write({
                "selling_price": offer.price,
                "buyer_id": offer.partner_id,
                "state": "offer_accepted"
            })
            

    def action_reject(self):
        for offer in self: 
            offer.status = 'refused'


    _sql_constraints = [
        (
            'check_offer_positive',
            'CHECK(price > 0)',
            'El precio de al oferta debe ser positivo'
        )
    ]





