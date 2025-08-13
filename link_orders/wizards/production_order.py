from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CreateMrpWizard(models.TransientModel):
    _name = 'create.mrp.wizard'
    _description = 'Wizard to Create MRP Orders for Selected Products'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, readonly=True)
    product_lines = fields.One2many('create.mrp.wizard.line', 'wizard_id', string='Products')

    def action_create_mrp_orders(self):
        MrpProduction = self.env['mrp.production']
        created_mrp_ids = []

        for line in self.product_lines:
            if line.select_product:
                if line.quantity > line.sale_order_line_id.balance_qty:
                    print('----------------------line.sale_order_line_id.balance_qty------------------------------', line.sale_order_line_id.balance_qty)
                    raise UserError(_(
                        "You cannot produce more than the remaining quantity for %s.\n"
                        "Remaining: %s, Requested: %s"
                    ) % (line.product_id.display_name, line.balance_quantity, line.quantity))

                mo = MrpProduction.create({
                    'product_id': line.product_id.id,
                    'product_qty': line.quantity,
                    'product_uom_id': line.product_id.uom_id.id,
                    'origin': self.sale_order_id.name,
                    'x_customer': self.sale_order_id.partner_id.id,
                    'pi_order_date': self.sale_order_id.date_order,
                    'delivery_date': self.sale_order_id.commitment_date,
                    'country_of_origin': self.sale_order_id.country_of_origin.id,
                    'shelf_life': self.sale_order_id.shelf_life,
                    'milk_origin': self.sale_order_id.milk_origin,
                })

                created_mrp_ids.append(mo.id)

        return {
            'name': 'Manufacturing Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_mrp_ids)],
            'context': {'default_origin': self.sale_order_id.name},
            'target': 'current',
        }

class CreateMrpWizardLine(models.TransientModel):
    _name = 'create.mrp.wizard.line'
    _description = 'Wizard Lines for MRP Orders'

    wizard_id = fields.Many2one('create.mrp.wizard', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    quantity = fields.Float(string='Quantity')
    select_product = fields.Boolean(string='Select')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    balance_quantity = fields.Float(string='Balance Quantity', compute='_compute_balance_quantity')

    @api.depends('sale_order_line_id')
    def _compute_balance_quantity(self):
        for line in self:
            print("---------_compute_balance_quantity-------------", self)
            line.balance_quantity = line.sale_order_line_id.balance_qty 
            print("--------- line.balance_quantity-------------", line.balance_quantity)
