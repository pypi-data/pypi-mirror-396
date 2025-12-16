# Copyright 2023 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    unvalued_picking_copy = fields.Boolean(
        default=False,
        help="Print an unvalued picking copy",
        copy=False,
    )
