from odoo import models, fields

class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    done_production_date = fields.Date(string='Production Date')