from odoo import models, fields

class EstatePropertyInherit(models.Model):
    _inherit = "estate.property"

    published_date = fields.Date(string="Fecha de publicacion")
    