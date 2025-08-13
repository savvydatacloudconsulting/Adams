from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    port_of_loading = fields.Char(string="Port of Loading")
    destination = fields.Char(string="Destination")
    shipping_document = fields.Char(string="Shipping Document")
    country_of_origin = fields.Many2one('res.country', string='Country of Origin')
    shelf_life = fields.Char(string='Shelf Life')
    milk_origin = fields.Char(string="Milk Origin")
    note_1 = fields.Text(string="Note 1")
    note_2 = fields.Text(string="Note 2")
    note_3 = fields.Text(string="Note 3")
    note_4 = fields.Text(string="Note 4")
    note_5 = fields.Text(string="Note 5")

    def action_send_proforma_invoice(self):
        self.ensure_one()
        template_id = self.env.ref('link_orders.report_custom_proforma_document').id
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True
        }
        return {
            'name': 'Send Pro-Forma Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


    # mrp_production_count = fields.Integer(
    #     string='Manufacturing Orders Count',
    #     compute='_compute_mrp_production_count'
    # )

    # def _compute_mrp_production_count(self):
    #     for order in self:
            
    #         print('------------------_compute_mrp_production_count----------------------------', self)

    def action_view_mrp_production(self):
        print("--------------action_view_mrp_production---------------", self)
        

    def action_create_mrp_order(self):
        self.ensure_one()

        # 🔑 Force fresh computes to get real balance_qty
        self.order_line._compute_produced_qty()
        self.order_line._compute_balance_qty()

        wizard = self.env['create.mrp.wizard'].create({
            'sale_order_id': self.id,
            'product_lines': [(0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.balance_qty,
                'sale_order_line_id': line.id,
            }) for line in self.order_line if line.balance_qty > 0]
        })
        return {
            'name': 'Create Manufacturing Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'create.mrp.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Assign sequence if not already provided
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.monthly') or _('New')
        return super().create(vals_list)



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    produced_qty = fields.Float(
        string="Produced Qty",
        compute="_compute_produced_qty",
        store=True
    )

    balance_qty = fields.Float(
        string="Balance Qty",
        compute="_compute_balance_qty",
        store=True
    )

    @api.depends('product_uom_qty', 'order_id.name')
    def _compute_produced_qty(self):
        Production = self.env['mrp.production']
        for line in self:
            mos = Production.search([
                ('origin', '=', line.order_id.name),
                ('product_id', '=', line.product_id.id)
            ])
            line.produced_qty = sum(mos.mapped('product_qty'))

    @api.depends('product_uom_qty', 'produced_qty')
    def _compute_balance_qty(self):
        for line in self:
            line.balance_qty = max(line.product_uom_qty - line.produced_qty, 0.0)
            print("-------------line.balance_qty---------------" , line.balance_qty)

