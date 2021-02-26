# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    analytic_count = fields.Integer(
        compute="_compute_analytic_ids",
        readonly=True,
    )
    analytic_account_ids = fields.One2many(
        comodel_name="account.analytic.account",
        compute="_compute_analytic_ids",
        string="Analytic Accounts",
        readonly=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
    )

    @api.depends("stock_request_ids")
    def _compute_analytic_ids(self):
        for req in self.sudo():
            req.analytic_account_ids = req.stock_request_ids.mapped(
                "analytic_account_id"
            )
            req.analytic_count = len(req.analytic_account_ids)

    def action_view_analytic(self):
        action = self.env.ref("analytic.action_account_analytic_account_form").read()[0]
        analytics = self.mapped("analytic_account_ids")
        if len(analytics) > 1:
            action["domain"] = [("id", "in", analytics.ids)]
        elif analytics:
            action["views"] = [
                (
                    self.env.ref("analytic.action_account_analytic_account_form").id,
                    "form",
                )
            ]
            action["res_id"] = analytics.id
        return action


class StockRequest(models.Model):
    _inherit = "stock.request"

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()
        self.analytic_account_id = self.order_id.analytic_account_id.id
        return res
