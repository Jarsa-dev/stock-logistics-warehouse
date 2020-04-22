# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.tools.float_utils import float_round


class StockProductSecondaryUnit(models.AbstractModel):
    _name = "stock.product.secondary.unit"
    _description = "Stock Product Secondary Unit"

    secondary_unit_qty_available = fields.Float(
        string="Quantity On Hand (2Unit)",
        compute="_compute_secondary_unit_qty_available",
        digits="Product Unit of Measure",
    )

    def _compute_secondary_unit_qty_available(self):

        for product in self:
            admin = self.env.ref('base.user_admin').id
            if not product.stock_secondary_uom_id:
                product.with_user(admin).secondary_unit_qty_available = 0.0
            else:
                qty = product.qty_available / (
                    product.stock_secondary_uom_id.factor or 1.0
                )
                product.with_user(admin).secondary_unit_qty_available = float_round(
                    qty, precision_rounding=product.uom_id.rounding
                )


class ProductTemplate(models.Model):
    _inherit = ["product.template", "stock.product.secondary.unit"]
    _name = "product.template"

    stock_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit", string="Second unit for inventory"
    )

    def _compute_quantities(self):
        super()._compute_quantities()
        self._compute_secondary_unit_qty_available()


class ProductProduct(models.Model):
    _inherit = ["product.product", "stock.product.secondary.unit"]
    _name = "product.product"

    def _compute_quantities(self):
        super()._compute_quantities()
        self._compute_secondary_unit_qty_available()
