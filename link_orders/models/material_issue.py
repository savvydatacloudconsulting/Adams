from odoo import models, fields, api
from odoo.exceptions import UserError

class MaterialIssue(models.Model):
    _name = 'material.issue'
    _description = 'Material Issue Form'
    _rec_name = 'lor_number'

    lor_number = fields.Char(string="LOR Number", readonly="1")
    date = fields.Date(string="Date")
    x_brand = fields.Char(string="Brand")
    production_order_numer = fields.Char(string="Production Order Number", readonly="1")
    product_tmpl_id = fields.Many2one('product.template', string="Product Description")
    pi_date = fields.Date(string="PI Date", readonly="1")
    pi_number = fields.Char(string='PI Number')
    x_customer = fields.Many2one('res.partner', string='Customer')
    milk_origin = fields.Char(string="Milk Origin")
    bom_id = fields.Many2one('mrp.bom', string="Bill of Materials")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    code = fields.Char(string="Document Reference Number", readonly="1")
    x_issue_number = fields.Char(string="Issue Number", readonly="1")
    x_issue_date = fields.Date(string="Issue Date", readonly="1")
    revision_no = fields.Char(string="Revision Number")
    x_revision_date = fields.Date(string="Revision Date")
    product_qty = fields.Float(string="Quantity")
    x_requested_by = fields.Many2one('res.users', string="Requested By")
    x_issued_by = fields.Many2one('res.users', string="Issued By")
    x_approved_by = fields.Many2one('res.users', string="Approved By")
    is_approved = fields.Boolean(string='Is Approved', default=False)
    is_confirmed = fields.Boolean(string='Is Confirmed', default=False)

    finished_goods_picking_id = fields.Many2one('stock.picking', string="Finished Goods Picking",   readonly=True,copy=False)

    bom_line_ids = fields.One2many('material.issue.line', 'issue_id', string="Material Lines")

    def action_approve(self):
        for bom in self:
            if bom.is_approved:
                raise UserError("This is already approved.")
            bom.approved_by = self.env.user
            bom.is_approved = True

    def action_confirm(self):
        for rec in self:
            if rec.is_confirmed:
                raise UserError("This is already confirmed.")
            rec.x_requested_by = self.env.user
            rec.is_confirmed = True

    def action_create_finished_goods_transfer(self):
        for issue in self:
            if issue.finished_goods_picking_id:
                raise UserError("Finished Goods Transfer already created.")

            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
            if not picking_type:
                raise UserError("No Receipt (Incoming) picking type found.")

            # Custom sequence
            new_name = self.env['ir.sequence'].next_by_code('stock.picking.internal.jc')

            picking = self.env['stock.picking'].create({
                'name': new_name,
                'picking_type_id': picking_type.id,
                'partner_id': issue.x_customer.id,
                'origin': f'FG Transfer for LOR {issue.lor_number}',
                'material_issue_id': issue.id,

                # === Additional Info Page fields ===
                'document_reference': issue.code,
                'x_issue_number': issue.x_issue_number,
                'x_issue_date': issue.x_issue_date,

                'revision_no': issue.revision_no,
                'x_revision_date': issue.x_revision_date,

                'production_order_number': issue.production_order_numer,
                'pi_date': issue.pi_date,

                'product_name': issue.product_tmpl_id.id,
                'ordered_qty': issue.product_qty,

                'milk_origin': issue.milk_origin,
                'utilization': sum(issue.bom_line_ids.mapped('utilization')),
                'finished_goods_qty': 0.0, 

                'x_requested_by': issue.x_requested_by.id,
                'x_issued_by': self.env.user.id,
                'x_approved_by': issue.x_approved_by.id,
                'is_approved': issue.is_approved,
                'is_confirmed': issue.is_confirmed,
            })

            # Create lines in receipt
            for line in issue.bom_line_ids:
                if not line.product_id:
                    continue

                self.env['stock.move'].create({
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.utilization,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'picking_id': picking.id,
                    'description_picking': line.product_id.description or '',
                })

            issue.finished_goods_picking_id = picking.id

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': picking.id,
                'target': 'current',
            }



    def action_open_finished_goods_picking(self):
        self.ensure_one()
        if not self.finished_goods_picking_id:
            raise UserError("No Finished Goods Picking linked.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Finished Goods Picking',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': self.finished_goods_picking_id.id,
            'target': 'current',
        }


class MaterialIssueLine(models.Model):
    _name = 'material.issue.line'
    _description = 'Material Issue Line'

    issue_id = fields.Many2one('material.issue', string="Material Issue")
    product_id = fields.Many2one('product.product', string="Material")
    product_qty = fields.Float(string="Issued Qty")
    return_to_store = fields.Float(string="Returned to Store")
    utilization = fields.Float(
        string="Utilization",
        compute='_compute_utilization',
        store=True
    )

    @api.depends('product_qty', 'return_to_store')
    def _compute_utilization(self):
        for line in self:
            line.utilization = line.product_qty - line.return_to_store if line.product_qty else 0.0

    @api.onchange('product_qty', 'return_to_store')
    def _onchange_utilization(self):
        for line in self:
            line.utilization = line.product_qty - line.return_to_store if line.product_qty else 0.0
