from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = "res.users"

    weight = fields.Float(string="Peso (kg)")

    estado_fisico = fields.Selection(
        selection=[
            ('malnourished', 'desnutrido'),
            ('healthy', 'saludable'),
            ('overweight','sobrepeso'),
        ],
        string="Estado Fisico",
        compute="_compute_estado_fisico",
        store=False,
    )
    

    @api.depends("weight")
    def _compute_estado_fisico(self):
        for record in self:
            if record.weight < 50:
                record.estado_fisico = 'malnourished'
            elif record.weight < 80:
                record.estado_fisico = 'healthy'
            else:
                record.estado_fisico = 'overweight'

    