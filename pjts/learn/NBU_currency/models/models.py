from datetime import timedelta, datetime
from odoo import fields, models
from NBU_currency.scraper.NBU_s_site_scraper.modules.NBY_api_parser import get_exchange_rate_by_date


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _create_EUR_dubl(self):
        eur_currency = self.create({
            'name': 'eur',
            'symbol': '€',
            'full_name': "EURO",
            'currency_unit_label': 'euro',
            'currency_subunit_label': 'cent',
            'rounding': 0.01,
            'active': True
        })

        return eur_currency

    def scrape_eur_rate_every_day(self):
        eur_currency = self.search([('name', '=', 'eur')], limit=1)
        if not eur_currency:
            eur_currency = self._create_EUR_dubl()

        end_date = fields.Date.today()
        start_date = end_date - timedelta(days=1)

        start_date_str = start_date.strftime("%d.%m.%Y")
        end_date_str = end_date.strftime("%d.%m.%Y")

        data = get_exchange_rate_by_date(
            startDate=start_date_str,
            endDate=end_date_str,
            is_save_json=False
        )

        for item in data.get("data", []):
            date_dt = datetime.strptime(item["date"], "%d.%m.%Y").date()
            rate_value = item.get("EUR", 0)

            if rate_value <= 0:
                continue

            existing_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', eur_currency.id),
                ('name', '=', date_dt)
            ], limit=1)

            rate_data = {
                'currency_id': eur_currency.id,
                'name': date_dt,
                'rate': 1.0 / rate_value
            }

            if existing_rate:
                existing_rate.write(rate_data)
            else:
                self.env['res.currency.rate'].create(rate_data)
