from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    x_lor_number = fields.Char(string="LOR Number", copy=False, readonly=True, index=True)
    document_reference_number = fields.Char(string='Document Reference Number', default="FRM-AD-72", readonly=True)
    x_issue_number = fields.Char(string='Issue No', default="02", readonly=True)
    x_issue_date = fields.Date(string='Issue Date', default="2021-10-31", readonly=True)
    x_revision_no = fields.Char(string='Revision No', default="02")
    x_revision_date = fields.Date(string='Revision Date', default="2023-10-31")
    x_requested_by = fields.Many2one('res.users', string='Requested By')
    x_issued_by = fields.Many2one('res.users', string='Issued By')
    x_approved_by = fields.Many2one('res.users', string='Approved By')
    is_approved = fields.Boolean(string='Is Approved', default=False)
    linked_mo_id = fields.Many2one('mrp.production', string='Linked MO')
    x_customer = fields.Many2one('res.partner', string='Customer')
    x_production_order_numer = fields.Char(string='PI Number')
    pi_order_date = fields.Date(string='PI Date')
    x_date = fields.Date(string='Created Date', default=fields.Date.context_today, readonly=True)
    x_brand = fields.Char(string="Brand")
    milk_origin = fields.Char(string="Milk Origin")
    is_confirmed = fields.Boolean(string='Is Confirmed', default=False)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('linked_mo_id'):
                vals['linked_mo_id'] = self.env.context.get('default_linked_mo_id')
            if not vals.get('x_lor_number'):
                vals['x_lor_number'] = self.env['ir.sequence'].next_by_code('mrp.bom.lot.number') or _('New')

        boms = super().create(vals_list)

        for bom, vals in zip(boms, vals_list):
            if vals.get('linked_mo_id'):
                mo = self.env['mrp.production'].browse(vals['linked_mo_id'])
                mo.bom_id = bom.id

        return boms

    def copy(self, default=None):
        default = dict(default or {})
        default['x_lor_number'] = self.env['ir.sequence'].next_by_code('mrp.bom.lot.number') or _('New')
        return super().copy(default)

    def action_approve(self):
        for bom in self:
            if bom.is_approved:
                raise UserError("This BOM is already approved.")
            bom.x_approved_by = self.env.user
            bom.is_approved = True

    def action_confirm(self):
        for rec in self:
            if rec.is_confirmed:
                raise UserError("This is already confirmed.")
            rec.x_requested_by = self.env.user
            rec.is_confirmed = True

    def action_create_material_issue(self):
        self.ensure_one()
        issue = self.env['material.issue'].create({
            'lor_number': self.x_lor_number,
            'date': fields.Date.context_today(self),
            'x_brand': self.x_brand,
            'production_order_numer': self.linked_mo_id.name if self.linked_mo_id else '',
            'product_tmpl_id': self.product_tmpl_id.id,
            'x_customer': self.x_customer.id,
            'pi_date': self.pi_order_date,
            'product_qty': self.product_qty,
            'pi_number': self.x_production_order_numer,
            'code': self.document_reference_number,
            'x_issue_number': self.x_issue_number,
            'x_issue_date': self.x_issue_date,
            'revision_no': self.x_revision_no,
            'x_revision_date': self.x_revision_date,
            'milk_origin': self.milk_origin,
            'x_issued_by': self.env.user.id,
            'bom_id': self.id,
        })

        for line in self.bom_line_ids:
            self.env['material.issue.line'].create({
                'issue_id': issue.id,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'return_to_store': 0.0,
                'utilization': 0.0,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Issue',
            'res_model': 'material.issue',
            'res_id': issue.id,
            'view_mode': 'form',
            'target': 'current',
        }


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    location_id = fields.Many2one('stock.location', string='Source Location')
    # lot_id = fields.Many2one('stock.production.lot', string='Lot / Batch', help="Lot number for this raw material")