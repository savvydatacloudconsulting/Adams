from odoo import models, fields, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Notes & Terms
    x_payment_terms = fields.Char(string="Payment Terms")
    x_delivery_term = fields.Char(string="Delivery Term")
    x_delivery_contact = fields.Char(string="Delivery Contact")
    order_type = fields.Selection([
        ('pending', 'Pending Orders'),
    ], string="Order Type", )

    # Notes
    x_note_1 = fields.Char(string="Note 1")
    x_note_2 = fields.Char(string="Note 2")
    x_note_3 = fields.Char(string="Note 3")
    x_note_4 = fields.Char(string="Note 4")
    x_note_5 = fields.Char(string="Note 5")
    x_note_6 = fields.Char(string="Note 6")
    x_note_7 = fields.Char(string="Note 7")
    x_notes_in_red = fields.Char(string="Notes In Red")
    x_note_8 = fields.Char(string="Note 8")
    x_note_9 = fields.Char(string="Note 9")
    x_note_10 = fields.Char(string="Note 10")
    x_note_11 = fields.Char(string="Note 11")
    x_note_12 = fields.Char(string="Note 12")
    x_note_13 = fields.Char(string="Note 13")
    x_note_14 = fields.Char(string="Note 14")
    x_note_15 = fields.Char(string="Note 15")
    x_note_16 = fields.Char(string="Note 16")
