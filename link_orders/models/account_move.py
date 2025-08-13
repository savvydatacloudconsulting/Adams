from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Shipping & Party Info
    x_notify_party = fields.Char(string="Notify Party")
    x_carriage_by = fields.Char(string="Carriage By")
    x_port_of_loading = fields.Char(string="Port Of Loading")
    x_port_of_discharge = fields.Char(string="Port Of Discharge")
    x_total_package = fields.Char(string="Total Package")

    # Notes
    x_is_notes = fields.Boolean(string="Is Notes?")
    x_note_1 = fields.Char(string="Note 1")
    x_note_2 = fields.Char(string="Note 2")
    x_note_3 = fields.Char(string="Note 3")
    x_note_4 = fields.Char(string="Note 4")
    x_note_5 = fields.Char(string="Note 5")
    x_note_6 = fields.Char(string="Note 6")

    # Additional Trade Info
    x_payment_terms = fields.Char(string="Payment Terms")
    x_incoterm = fields.Char(string="Incoterm")
    x_country_of_origin = fields.Many2one('res.country', string='Country of Origin')
    x_total_containers = fields.Char(string="Total Containers")
    x_hs_code = fields.Char(string="HS Code")

    # Labels
    x_is_label = fields.Boolean(string="Is Label?")
    x_label_1 = fields.Char(string="Label 1")
    x_label_2 = fields.Char(string="Label 2")
    x_label_3 = fields.Char(string="Label 3")
