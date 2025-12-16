# Copyright 2023 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    unvalued_copy = fields.Boolean(
        copy=False,
        help="Print an unvalued picking copy",
    )

    @api.model_create_multi
    def create(self, vals_list):
        partner_model = self.env["res.partner"]
        for vals in vals_list:
            partner = partner_model.browse(vals.get("partner_id"))
            if partner.exists():
                vals["unvalued_copy"] = partner.unvalued_picking_copy
        return super().create(vals_list)
