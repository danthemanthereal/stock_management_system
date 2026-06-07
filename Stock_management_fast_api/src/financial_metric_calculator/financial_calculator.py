from sqlalchemy.ext.asyncio import AsyncSession


class FinancialMetricCalculator:
    def __init__(self, total_financial_metric_map, db: AsyncSession):
        self.total_financial_metric_map = total_financial_metric_map
        self.db = db
        self.financial_metrics_handler = self.init_financial_metrics_handler()


    def init_financial_metrics_handler(self):
        metric_handlers = {
            "cost_of_goods_and_service_sold_to_revenue": self.get_cost_of_goods_and_service_sold_to_revenue_last_four_years,
          #  "salesGeneralAndAdministrativeToRevenue": self.get_sales_and_administrative_to_revenue_last_four_years,
           # "cost_of_revenue_to_revenue":self.get_cost_of_revenue_to_revenue_last_four_years,
            #"researchAndDevelopementToRevenue": self.get_research_and_development_to_revenue_last_four_years,
            "cash_conversion_cycle": self.get_cash_conversion_cycle_last_four_years,
            "cash_ratio": self.get_cash_ratio_last_four_years,
            "current_ratio":self.get_current_ratio_last_four_years,
            "days_inventory": self.get_days_inventory_last_four_years,
            "days_payable": self.get_days_payable_last_four_years,
            "days_sales_outstanding": self.get_days_sales_outstanding_last_four_years,
           # "defensive_interval_ratio": "",
            "inventory_to_revenue": self.get_inventory_to_revenue_last_four_years,
            "inventory_turnover": self.get_inventory_turnover_last_four_years,
            "quick_ratio": self.get_quick_ratio_last_four_years,
            "receivables_turnover": self.get_receivables_turnover_last_four_years,
            "turnover": self.get_turnover_last_four_years,
          #  "payablesTurnover": "",
          #  "fixedAssetTurnover": "",
          #  "cover_sales_in_days": "",
         #   "book_to_bill_ratio": "",
            "capex_to_operating_cash_flow": self.get_capex_to_operating_cash_flow_last_four_years,
            "capex_to_operating_income": self.get_capex_to_operating_income_last_four_years,
            "capex_to_revenue": self.get_capex_to_revenue_last_four_years,
            "debt_to_asset":self.get_debt_to_asset_last_four_years_last_four_years,
            "debt_to_equity":self.get_debt_to_equity_last_four_years_last_four_years,
            "equity_to_asset": self.get_equity_to_asset_ratio_last_four_years,
            "interest_coverage": self.get_interest_coverage_last_four_years,
          #  "liabilities_to_assets": self.get_liabilities_to_asset_ratio_last_four_years,
            "sloan_ratio": self.get_sloan_ratio_last_four_years,
         #   "netDebtToEBITDA": "",
         #   "solvencyRatio": "",
         #   "debtToCapitalRatio": "",
          #  "longTermDebtToCapitalRatio": "",
        #    "debtServiceCoverageRatio": "",
         #   "shortTermOperatingCashFlowCoverageRatio": "",
         #   "operatingCashFlowCoverageRatio": "",
        #    "capitalExpenditureCoverageRatio": "",
            "gearing":self.get_gearing_last_four_years,
            "dynamic_debt_degree":self.get_dynamic_debt_degree_last_four_years,
            "current_asset_intensity": "",
            "non_current_asset_intensity": "",
            "asset_cover_ratio_one": "",
            "asset_cover_ratio_two": "",
            "good_will_ratio": "",
          #  "investment_to_operative_cashflow": "",
            "useless_degree": "",
            "growth_ratio": "",
            "cash_burn_rate": "",
            "fscore": "",
            "gf_score": "",
            "gf_value": "",
            "graham_number": "",
            "mscore": "",
            "price_to_gf_value": "",
            "rank_balancesheet": "",
            "rank_gf_value": "",
            "rank_growth": "",
            "rank_momentum": "",
            "rank_predictability": "",
            "rank_profitability": "",
            "zscore": "",
            "daysOfPayablesOutstanding": "",
            "daysOfInventoryOutstanding": "",
            "workingCapitalTurnoverRatio": "",
            "dividendPaidAndCapexCoverageRatio": "",
            "dividends": "",
            "dividends_per_share": "",
            "ebitda_margin": "",
            "fcf_margin": "",
            "fcf_yield": "",
            "gross_margin": "",
            "gross_profit_to_asset": "",
            "net_margin": "",
            "ocf_margin": "",
            "ocf_yield": "",
            "operating_margin": "",
            "return_on_tangible_asset": "",
            "return_on_tangible_equity": "",
            "roa": "",
            "roce": "",
            "roe": "",
            "roic": "",
            "yield": "",
            "freeCashFlowToEquity": "",
            "freeCashFlowToFirm": "",
            "ebit_margin": "",
            "operatingProfitMargin": "",
            "pretaxProfitMargin": "",
            "netProfitMargin": "",
            "operatingCashFlowRatio": "",
            "operatingCashFlowSalesRatio": "",
            "freeCashFlowOperatingCashFlowRatio": "",
            "revenue_per_employee": "",
            "roi": "",
            "capital_turnover": "",
            "cash_per_share": "",
            "ebitda_per_share": "",
            "enterprise_value_to_ebit": "",
            "enterprise_value_to_ebitda": "",
            "enterprise_value_to_fcf": "",
            "enterprise_value_to_ocf": "",
            "enterprise_value_to_revenue": "",
            "free_cash_flow_per_share": "",
            "growth_per_share_ebitda": "",
            "growth_per_share_eps": "",
            "growth_revenue_per_share": "",
            "net_cash_per_share": "",
            "pb_ratio": "",
            "pe_ratio": "",
            "peg_ratio": "",
            "peter_lynch_fair_value": "",
            "price_to_free_cash_flow": "",
            "price_to_operating_cash_flow": "",
            "price_to_owner_earnings": "",
            "price_to_tangible_book": "",
            "ps_ratio": "",
            "revenue_per_share": "",
            "degree_of_financial_leverage": "",
            "degree_of_operating_leverage": "",
            "capexToDepreciation": "",
            "intangiblesToTotalAssets": "",
            "financialLeverageRatio": "",
            "wacc": ""
        }
        return metric_handlers

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

    def get_cost_of_goods_and_service_sold_to_revenue_last_four_years(self):
        #return self.calculate_to_revenue_ratio("costofGoodsAndServicesSold")
        return self.total_financial_metric_map.get("cost_of_goods_sold_to_revenue", [])

    def get_sales_and_administrative_to_revenue_last_four_years(self):

        #return self.calculate_to_revenue_ratio("sellingGeneralAndAdministrative")
        #return self.total_financial_metric_map.get("cost_of_goods_sold_to_revenue", [])
        pass

    def get_cost_of_revenue_to_revenue_last_four_years(self):
        #return self.calculate_to_revenue_ratio("costOfRevenue")
        pass

    def get_research_and_development_to_revenue_last_four_years(self):
        #return self.calculate_to_revenue_ratio("researchAndDevelopment")
        pass

    def get_cash_conversion_cycle_last_four_years(self):
        pass

    def get_cash_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("cash_ratio", [])

    def get_current_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("current_ratio", [])

    def get_days_inventory_last_four_years(self):
        return self.total_financial_metric_map.get("days_inventory", [])

    def get_days_payable_last_four_years(self):
        return self.total_financial_metric_map.get("days_payable", [])

    def get_days_sales_outstanding_last_four_years(self):
        return self.total_financial_metric_map.get("days_sales_outstanding", [])

    def get_inventory_to_revenue_last_four_years(self):
        return self.total_financial_metric_map.get("inventory_to_revenue", [])

    def get_inventory_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("inventory_turnover", [])

    def get_quick_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("quick_ratio", [])

    def get_receivables_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("receivables_turnover", [])

    def get_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("turnover", [])

    def get_payables_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("payablesTurnover", [])

    def get_capex_to_operating_cash_flow_last_four_years(self):
        return self.total_financial_metric_map.get("get_capex_to_operating_cash_flow", [])

    def get_capex_to_operating_income_last_four_years(self):
        return self.total_financial_metric_map.get("capex_to_operating_income", [])

    def get_capex_to_revenue_last_four_years(self):
        return self.total_financial_metric_map.get("capex_to_revenue", [])

    def get_debt_to_asset_last_four_years_last_four_years(self):

        #return self.debt_to_metric_ratio_last_four_years("totalAssets")
        return self.total_financial_metric_map.get("debt_to_asset", [])

    def get_debt_to_equity_last_four_years_last_four_years(self):
        #return self.debt_to_metric_ratio_last_four_years("totalShareholderEquity")
        return self.total_financial_metric_map.get("debt_to_equity", [])

    def get_equity_to_asset_ratio_last_four_years(self):

        #return self.get_value_to_asset_ratio_last_four_years("totalShareholderEquity")
        return self.total_financial_metric_map.get("equity_to_asset", [])

    def get_interest_coverage_last_four_years(self):
        return self.total_financial_metric_map.get("interest_coverage", [])

    def get_liabilities_to_asset_ratio_last_four_years(self):

        #return self.get_value_to_asset_ratio_last_four_years("totalLiabilities")
        pass

    def get_sloan_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("sloan_ratio", [])



    def calculate_to_revenue_ratio_last_four_years(self, metric_key):

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


    def get_debt_to_capital_last_four_years_last_four_years(self):
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

    def debt_to_metric_ratio_last_four_years(self, metric_key):

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


    def get_value_to_asset_ratio_last_four_years(self, value:str):
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
        total_liabilities_last_four_years = self.total_financial_metric_map.get("total_liabilities", [])
        cash_and_equivalents_last_four_years = self.total_financial_metric_map.get("cash_and_cash_equivalents", [])
        equity_last_four_years = self.total_financial_metric_map.get("total_equity", [])

        gearing_last_four_years = []

        for idx, val in enumerate(total_liabilities_last_four_years):
            current_liability = float(val)
            current_cash_and_equivalents = float(cash_and_equivalents_last_four_years[idx])
            current_equity = float(equity_last_four_years[idx])
            val_float = current_liability - current_cash_and_equivalents
            ratio = round(val_float / current_equity, 2) if current_equity != 0 else None
            gearing_last_four_years.append(ratio)
        return gearing_last_four_years

    def get_dynamic_debt_degree_last_four_years(self):
        pass





