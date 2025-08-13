from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    x_logo = fields.Binary(string="Secondary Logo", readonly=False)
    x_po_box = fields.Char(string="P.O. Box")
