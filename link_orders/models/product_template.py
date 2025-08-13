from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    production_date = fields.Date(string='Production Date')
    expiry_date = fields.Date(string='Expiry Date')
    batch_no = fields.Char(string='Batch Number')
    code = fields.Char(string='Code')


class Product(models.Model):
    _inherit = 'product.product'

    production_date = fields.Date(string='Production Date')
    expiry_date = fields.Date(string='Expiry Date')
    batch_no = fields.Char(string='Batch Number')
    code = fields.Char(string='Code')