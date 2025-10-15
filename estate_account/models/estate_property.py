from odoo import models, fields

class EstateProperty(models.Model):
    _inherit ="estate.property"


    def action_sold(self):
        
        #Llamamos primer al metodo original
        result = super().action_sold()

        for property in self:

            #Creamos una factura con lineas incluidas
            invoice = self.env["account.move"].create({
                "partner_id": property.buyer_id.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    #Linea para comision del 6%
                    (0,0, {
                        "name": "Comision por venta de propiedad 6%",
                        "quantity":1,
                        "price_unit": property.selling_price * 0.06,
                    }),
                    #Linea por gastos administrativos fijos
                    (0,0, {
                        "name": "Gastos administrativos",
                        "quantity": 1,
                        "price_unit": 100.00
                    })
                ]
            })
            print(f"Factura creada: {invoice.id} para {self.buyer_id.name}" )

        return result   
