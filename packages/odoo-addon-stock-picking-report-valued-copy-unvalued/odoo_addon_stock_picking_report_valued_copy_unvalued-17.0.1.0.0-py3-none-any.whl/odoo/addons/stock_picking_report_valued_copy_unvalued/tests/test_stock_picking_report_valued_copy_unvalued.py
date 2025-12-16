# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingCreate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.Picking = cls.env["stock.picking"]

        cls.partner_true = cls.Partner.create(
            {
                "name": "Partner True",
                "unvalued_picking_copy": True,
            }
        )

        cls.partner_false = cls.Partner.create(
            {
                "name": "Partner False",
                "unvalued_picking_copy": False,
            }
        )

        cls.base_vals = {
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
            "picking_type_id": cls.env.ref("stock.picking_type_out").id,
        }

    def test_create_sets_unvalued_copy_true(self):
        """The picking should copy unvalued_copy=True from the partner."""
        picking = self.Picking.create(
            {
                **self.base_vals,
                "partner_id": self.partner_true.id,
            }
        )
        self.assertTrue(
            picking.unvalued_copy,
            "The picking should copy unvalued_copy=True from the partner.",
        )

    def test_create_sets_unvalued_copy_false(self):
        """The picking should copy unvalued_copy=False from the partner."""
        picking = self.Picking.create(
            {
                **self.base_vals,
                "partner_id": self.partner_false.id,
            }
        )
        self.assertFalse(
            picking.unvalued_copy,
            "The picking should copy unvalued_copy=False from the partner.",
        )
