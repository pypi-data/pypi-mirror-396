# Copyright 2023 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Report with Unvalued Copy",
    "summary": "Print valued and unvalued delivery slip at the same time",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/sygel-technology/sy-stock-logistics-reporting",
    "author": "Alberto Martínez, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_picking_report_valued",
    ],
    "data": [
        "report/stock_picking_report.xml",
        "views/res_partner_views.xml",
        "views/stock_picking_views.xml",
    ],
}
