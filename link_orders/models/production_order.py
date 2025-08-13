from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    x_customer = fields.Many2one('res.partner', string="Customer")
    pi_order_date = fields.Date(string="PI Date", readonly=True)
    document_reference_number = fields.Char(string='Document Reference Number', default="FRM-AD-72", readonly=True)
    x_issue_number = fields.Char(string='Issue No', default="02", readonly=True)
    x_issue_date = fields.Date(string='Issue Date', default="2021-10-31", readonly=True)
    revision_number = fields.Char(string='Revision No', default="02")
    x_revision_date = fields.Date(string='Revision Date', default="2023-10-31")
    packing_size = fields.Char(string='Packing Size')
    packing_requirenment = fields.Text(string='Packing Requirement')
    country_of_origin = fields.Many2one('res.country', string='Country of Origin')
    shelf_life = fields.Char(string='Shelf Life')
    milk_origin = fields.Char(string="Milk Origin")

    product_quality = fields.Char(string='Product Quality')
    delivery_date = fields.Date(string='Delivery Date')
    loading_description = fields.Text(string='Loading Description')
    x_requested_by = fields.Many2one('res.users', string='Requested By')
    x_issued_by = fields.Many2one('res.users', string='Issued By')
    x_approved_by = fields.Many2one('res.users', string='Approved By')
    is_approved = fields.Boolean(string='Is Approved', default=False)

    @api.model
    def create(self, vals):
        if not vals.get('x_requested_by'):
            vals['x_requested_by'] = self.env.uid
        return super().create(vals)

    def action_confirm(self):
        for mo in self:
            mo.x_issued_by = self.env.user
        return super().action_confirm()

    def action_approve(self):
        for mo in self:
            if mo.is_approved:
                raise UserError("This Manufacturing Order is already approved.")
            mo.x_approved_by = self.env.user
            mo.is_approved = True

    def action_create_bom(self):
        self.ensure_one()
        return {
            'name': 'Create BOM',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'form',
            'context': {
                'default_product_tmpl_id': self.product_tmpl_id.id,
                'default_product_id': self.product_id.id,
                'default_linked_mo_id': self.id,
                'default_x_customer': self.x_customer.id,
                'default_x_production_order_numer': self.origin,
                'default_pi_order_date': self.pi_order_date,
                'default_milk_origin': self.milk_origin,
                'default_x_issued_by': self.env.user.id,  # ✅
                # 'default_location_id': self.location_id.id,  # ✅ added this

            },
            'target': 'current',
        }

