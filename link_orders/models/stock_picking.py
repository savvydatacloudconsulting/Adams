from odoo import models, fields
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    material_issue_id = fields.Many2one('material.issue', string='Material Issue')

    document_reference = fields.Char(string="Document Reference Number", readonly=True)
    x_issue_number = fields.Char(string="Issue Number", readonly=True)
    x_issue_date = fields.Date(string="Issue Date", readonly=True)

    revision_no = fields.Char(string="Revision Number")
    x_revision_date = fields.Date(string="Revision Date")

    production_order_number = fields.Char(string="Production Order Number", readonly=True)
    pi_date = fields.Date(string="PI Date", readonly="1")

    product_name = fields.Many2one('product.template', string="Product", readonly=True)

    ordered_qty = fields.Float(string="Ordered Quantity", readonly=True)
    batch_lot_number = fields.Char(string="Batch/Lot Number")
    milk_origin = fields.Char(string="Milk Origin")
    finished_goods_qty = fields.Float(string="Finished Goods Quantity")
    utilization = fields.Float(string="Utilization")
    milk_origin = fields.Char(string="Milk Origin")

    x_requested_by = fields.Many2one('res.users', string="Requested By")
    x_issued_by = fields.Many2one('res.users', string="Issued By")
    x_approved_by = fields.Many2one('res.users', string="Approved By")
    is_approved = fields.Boolean(string='Is Approved', default=False)
    is_confirmed = fields.Boolean(string='Is Confirmed', default=False)
    note_1 = fields.Char(string="Note 1")
    note_2 = fields.Char(string="Note 2")

    def action_approve(self):
        for bom in self:
            if bom.is_approved:
                raise UserError("This is already approved.")
            bom.x_approved_by = self.env.user
            bom.is_approved = True

    def action_confirm(self):
        for rec in self:
            if rec.is_confirmed:
                raise UserError("This is already confirmed.")
            rec.x_requested_by = self.env.user
            rec.is_confirmed = True