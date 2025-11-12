# Copyright 2025 Quanimacy
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"

    month_based = fields.Boolean(
        string="Month Based Calculation",
        help="If checked, the depreciation will be calculated from the first day "
        "of the asset's start month, ignoring the specific start day.",
    )
