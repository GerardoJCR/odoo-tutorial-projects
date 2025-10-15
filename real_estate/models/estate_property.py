from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
# from datetime import timedelta # trabajar dias, horas, minutos, segundos
from dateutil.relativedelta import relativedelta #  years, months, days, leapdays, weeks, hours, minutes, seconds, microseconds,
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Propiedad Inmobiliaria"
    _order = "id desc" #orden descendiente 

    #Campos basicos
    name = fields.Char(default="Casita" , required=True)
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    description = fields.Text(string="Descripción")
    postcode = fields.Char(string="Código Postal")
    date_availability = fields.Date(string="Fecha de Disponibilidad", copy=False, default=fields.Date.today() + relativedelta(months=3)) 
    expected_price = fields.Float(string="Precio Esperado", copy=False)
    # expected_price = fields.Float(string="Precio Esperado", required=True, copy=False, default=100)
    selling_price = fields.Float(string="Precio de Venta", readonly=True, copy=False)
    active = fields.Boolean(string="Active", default=True)
    bedrooms = fields.Integer(string="Dormitorios", default=2)
    living_area = fields.Integer(string="Área de Estar (m²)")
    facades = fields.Integer(string="Fachadas")
    garage = fields.Boolean(string="¿Tiene Cochera?")
    garden = fields.Boolean(string="¿Tiene Jardín?")
    garden_area = fields.Integer(string="Área del Jardín (m²)")
    garden_orientation = fields.Selection(
        string="Orientación del Jardín",
        selection=[
            ('north', 'Norte'),
            ('south', 'Sur'),
            ('east', 'Este'),
            ('west', 'Oeste'),
        ],
        help="Selecciona hacia dónde está orientado el jardín"
    )
    state = fields.Selection(
        string= "Estado",
        selection=[
            ("new", "Nuevo"),
            ("offer_received", "Oferta Recibida "),
            ("offer_accepted", "Oferta Aceptada"),
            ("sold", "Vendida"),
            ("canceled", "Cancelada"),
        ],
        default='new',
        copy= False,
        required=True,
        readonly=True
    )
    #Campos Relacionales
    property_type_id = fields.Many2one(comodel_name="estate.property.type", string="Tipo de Propiedad")
    seller_id = fields.Many2one(comodel_name="res.users", string="Vendedor", readonly=True, default=lambda self: self.env.user)
    buyer_id = fields.Many2one(comodel_name="res.partner", string="Comprador", readonly=True, )
    tag_ids = fields.Many2many(comodel_name="estate.property.tag", string="Etiquetas")
    offer_ids = fields.One2many(comodel_name="estate.property.offer" ,inverse_name="property_id")
    #campos computados
    total_area =fields.Integer(
        string ="Total Area(m2)",
        compute= "_compute_total_area",
        store= True 
    )
    best_price = fields.Float(
        string="Mejor Oferta",
        compute="_compute_best_price",
        store=True
    )
    #restricciones sql
    _sql_constraints  = [
        ('expected_price_positive','CHECK (expected_price > 0)','El precio esperado deber ser positivo'),
        ('selling_price_positive','CHECK (selling_price >= 0)','El precio de venta debe ser positivo'
        )
    ]

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        for record in self: 
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            #Obtener todos los precios de las ofertas
            prices = record.offer_ids.mapped('price')
            #Asignar el maximo a 0 si no hay errores
            record.best_price = max(prices) if prices else 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        # Actualiza automaticamente los valores del jardin cuando cambia
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden = True
                record.garden_orientation = 'north'
            else:
                record.garden_area = 0
                record.garden_orientation = False


    #Evitamos eliminacion si no esta 'new' o 'canceled'
    @api.ondelete(at_uninstall=False)
    def _check_property_deletion(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError(
                    f"No puedes eliminar la propiedad '{record.name}'"
                    f"porque su estado es '{record.state}'"
                )
    #acciones
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("No puedes cancelar una propiedad vendida")
            record.state= 'canceled'

    def action_sold(self):
        for record in self: 
            if record.state == 'canceled':
                raise UserError("No puedes vender una propiedad cancelada")
            record.state = 'sold'



    #restricciones
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        """Evita que el precio de venta sea menor al 90% del precio esperado."""
        for record in self:
            
            if float_is_zero(record.selling_price, precision_digits=2):
                continue

            # Calcular el 90% del precio esperado
            min_price = record.expected_price * 0.9

            # Comparar usando float_compare para evitar errores de precisión
            if float_compare(record.selling_price, min_price, precision_digits=2) < 0:
                raise ValidationError(
                    "El precio de venta no puede ser inferior al 90% del precio esperado."
                )

