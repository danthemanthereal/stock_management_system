from sqlalchemy.ext.asyncio import AsyncSession


class FinancialMetricCalculator:
    def __init__(self, total_financial_metric_map, db: AsyncSession):
        self.total_financial_metric_map = total_financial_metric_map
        self.db = db
        self.financial_metrics_handler = self.init_financial_metrics_handler()


    def init_financial_metrics_handler(self):
        metric_handlers = {
            "cost_of_goods_and_service_sold_to_revenue": self.get_cost_of_goods_and_service_sold_to_revenue,
            "salesGeneralAndAdministrativeToRevenue": self.get_sales_and_administrative_to_revenue,
            "cost_of_revenue_to_revenue":self.get_cost_of_revenue_to_revenue,
            "researchAndDevelopementToRevenue": self.get_research_and_development_to_revenue,
            "debt_to_asset":self.get_debt_to_asset_last_four_years,
            "debt_to_equity":self.get_debt_to_equity_last_four_years,
            "debtToCapitalRatio"
            "equity_to_asset": self.get_equity_to_asset_ratio,
            "liabilities_to_assets": self.get_liabilities_to_asset_ratio,
            "gearing":self.get_gearing_last_four_years,
             "dynamic_debt_degree":

        }
        return metric_handlers

    def get_cost_of_goods_and_service_sold_to_revenue(self):
        return self.calculate_to_revenue_ratio("costofGoodsAndServicesSold")

    def get_sales_and_administrative_to_revenue(self):
        return self.calculate_to_revenue_ratio("sellingGeneralAndAdministrative")

    def get_cost_of_revenue_to_revenue(self):
        return self.calculate_to_revenue_ratio("costOfRevenue")

    def get_research_and_development_to_revenue(self):
        return self.calculate_to_revenue_ratio("researchAndDevelopment")

    def calculate_to_revenue_ratio(self, metric_key):

        values = self.total_financial_metric_map.get(metric_key, [])
        revenues = self.total_financial_metric_map.get("totalRevenue", [])

        result = []
        for val, rev in zip(values, revenues):
            try:
                rev_float = float(rev)
                val_float = float(val)
                ratio = round(val_float / rev_float * 100, 2) if rev_float != 0 else None
            except (ValueError, TypeError):
                ratio = None
            result.append(ratio)
        return result

    def get_debt_to_asset_last_four_years(self):

        return self.debt_to_metric_ratio("totalAssets")

    def get_debt_to_equity_last_four_years(self):
        return self.debt_to_metric_ratio("totalShareholderEquity")

    def get_debt_to_capital_last_four_years(self):
        debts = self.get_total_debt_last_four_years()
        values = self.total_financial_metric_map.get("totalShareholderEquity", [])

        result = []
        for debt, val in zip(values, debts):
            try:
                debt_float = float(debt)
                val_float = float(val)
                val_float  += debt_float
                ratio = round(debt_float / val_float, 2) if val_float != 0 else None
            except (ValueError, TypeError):
                ratio = None
            result.append(ratio)
        return result

    def get_total_debt_last_four_years(self):
        short_term_debt_last_four_years = self.total_financial_metric_map.get("shortTermDebt", [])
        capital_lease_obligations_last_four_years = self.total_financial_metric_map.get("capitalLeaseObligations", [])
        long_term_debt_last_four_years = self.total_financial_metric_map.get("longTermDebt", [])

        total_debt_last_four_years =  [float(s)+float(c)+float(l) for s,c,l in zip(short_term_debt_last_four_years, capital_lease_obligations_last_four_years,long_term_debt_last_four_years)]
        return total_debt_last_four_years

    def debt_to_metric_ratio(self, metric_key):

        debts = self.get_total_debt_last_four_years()
        values = self.total_financial_metric_map.get(metric_key, [])

        result = []
        for debt, val in zip(values, debts):
            try:
                debt_float = float(debt)
                val_float = float(val)
                ratio = round(debt_float / val_float, 2) if val_float != 0 else None
            except (ValueError, TypeError):
                ratio = None
            result.append(ratio)
        return result

    def get_equity_to_asset_ratio(self):

        return self.get_value_to_asset_ratio("totalShareholderEquity")

    def get_liabilities_to_asset_ratio(self):

        return self.get_value_to_asset_ratio("totalLiabilities")

    def get_value_to_asset_ratio(self, value:str):
        value_last_four_years = self.total_financial_metric_map.get(value, [])
        assets_last_four_years = self.total_financial_metric_map.get("totalAssets", [])

        equity_to_asset_last_four_years = []

        for val, asset in zip(value_last_four_years, assets_last_four_years):
            try:
                val_float = float(val)
                asset_float = float(asset)
                ratio = round(val_float / asset_float, 2) if asset_float != 0 else None
            except (ValueError, TypeError):
                ratio = None
            equity_to_asset_last_four_years.append(ratio)
        return equity_to_asset_last_four_years

    def get_gearing_last_four_years(self):
        total_liabilities_last_four_years = self.total_financial_metric_map.get("totalLiabilities'", [])
        cash_and_equivalents_last_four_years = self.total_financial_metric_map.get("cashAndCashEquivalentsAtCarryingValue", [])
        equity_last_four_years = self.total_financial_metric_map.get("totalShareholderEquity", [])

        gearing_last_four_years = []

        for idx, val in enumerate(total_liabilities_last_four_years):
            current_liability = float(val)
            current_cash_and_equivalents = float(cash_and_equivalents_last_four_years[idx])
            current_equity = float(equity_last_four_years[idx])
            val_float = current_liability - current_cash_and_equivalents
            ratio = round(val_float / current_equity * 100, 2) if current_equity != 0 else None
            gearing_last_four_years.append(ratio)
        return gearing_last_four_years

    def get_dynamic_debt_degree_last_four_years(self):
        pass

    async def get_calculated_financial_metric_map(self):
        calculated_financial_metric_map = {}
        financial_metrics_to_calculate = await self.get_calculated_financial_metrics()
        print("total map")
        print(self.total_financial_metric_map)
        for financial_metric in financial_metrics_to_calculate:
            try:
                handler = self.financial_metrics_handler.get(financial_metric)

                if handler:
                    calculated_financial_metric_map[financial_metric] =  handler()
                else:
                    calculated_financial_metric_map[financial_metric] = []

            except Exception as e:
                print(e)
                continue

        return calculated_financial_metric_map


    async def get_calculated_financial_metrics(self) -> list[str]:

        FINANCIAL_METRIC_CATEGORIES = [
            "Aufwandsquote",
            "Working Capital Management",
            "Finanzielle Stabilität",
            "Rentabilität",
            "Bewertungskennzahl"
        ]
        calculated_financial_metrics = []

        from src.financial_metric_analysis_component.financial_metric_service import MetricsService

        metric_service = MetricsService(self.db)

        for category in FINANCIAL_METRIC_CATEGORIES:
            calculated_financial_metrics_current_category = await metric_service.get_metrics_by_category_name(category)
            calculated_financial_metrics.extend(calculated_financial_metrics_current_category)

        return calculated_financial_metrics




