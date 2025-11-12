# Copyright 2025 Quanimacy
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons.account_asset_management.models.account_asset import READONLY_STATES


class AccountAsset(models.Model):
    _inherit = "account.asset"

    move_id = fields.Many2one(
        "account.move",
        string="Invoice",
        domain="[('move_type', '=', 'in_invoice'),('partner_id', '=', partner_id)]",
        states=READONLY_STATES,
    )

    month_based = fields.Boolean(
        string="Month Based Calculation",
        compute="_compute_month_based",
        store=True,
        readonly=False,
        help="If checked, the depreciation will be calculated from the first day "
        "of the asset's start month, ignoring the specific start day.",
    )

    @api.depends("profile_id")
    def _compute_month_based(self):
        for asset in self:
            if asset.profile_id:
                asset.month_based = asset.profile_id.month_based
            else:
                asset.month_based = False

    def _get_depreciation_start_date(self, fy):
        if self.month_based:
            return self.date_start.replace(day=1)
        return super()._get_depreciation_start_date(fy)

    def _get_first_period_amount(
        self, table, entry, depreciation_start_date, line_dates
    ):
        """
        Return prorata amount for Time Method 'Year' in case of 'Month Based'.
        """
        if self.month_based and self.method_time == "year":
            # For month-based calculation, prorate the first year's amount
            # based on the number of remaining months in the fiscal year.
            remaining_months = 12 - depreciation_start_date.month + 1
            return (entry["period_amount"] / 12) * remaining_months

        return super()._get_first_period_amount(
            table, entry, depreciation_start_date, line_dates
        )

    def _get_fy_duration_factor(self, entry, firstyear):
        """
        Calculate the fiscal year duration factor based on months for month-based assets.
        """
        if self.month_based and firstyear:
            depreciation_start_date = self.date_start.replace(day=1)
            remaining_months = 12 - depreciation_start_date.month + 1
            return float(remaining_months) / 12
        return super()._get_fy_duration_factor(entry, firstyear)

    def _get_depreciation_stop_date(self, depreciation_start_date):
        """
        Adjust stop date for prorata and month_based calculations.
        """
        if (
            (self.prorata or self.month_based)
            and self.method_time == "year"
            and not self.method_end
        ):
            depreciation_stop_date = depreciation_start_date + relativedelta(years=self.method_number-1)
            return depreciation_stop_date
        return super()._get_depreciation_stop_date(depreciation_start_date)
