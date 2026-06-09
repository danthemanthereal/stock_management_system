from fin_ratios import free_cash_flow, operating_cash_flow_ratio, capex_to_depreciation
from sqlalchemy.ext.asyncio import AsyncSession


class FinancialMetricCalculator:
    def __init__(self, total_financial_metric_map, db: AsyncSession):
        self.total_financial_metric_map = total_financial_metric_map
        self.db = db
        self.financial_metrics_handler = self.init_financial_metrics_handler()


    def init_financial_metrics_handler(self):
        metric_handlers = {
            "cost_of_goods_and_service_sold_to_revenue": self.get_cost_of_goods_and_service_sold_to_revenue_last_four_years,
            "sales_general_and_administrative_to_revenue": self.get_sales_and_administrative_to_revenue_last_four_years,
            "cost_of_revenue_to_revenue":self.get_cost_of_revenue_to_revenue_last_four_years,
            "research_and_developement_to_revenue": self.get_research_and_development_to_revenue_last_four_years,
            "cash_conversion_cycle": self.get_cash_conversion_cycle_last_four_years,
            "cash_ratio": self.get_cash_ratio_last_four_years,
            "current_ratio":self.get_current_ratio_last_four_years,
            "days_inventory": self.get_days_inventory_last_four_years,
            "days_payable": self.get_days_payable_last_four_years,
            "days_sales_outstanding": self.get_days_sales_outstanding_last_four_years,
            "defensive_interval_ratio": self.get_defensive_interval_ratio_last_four_years,
            "inventory_to_revenue": self.get_inventory_to_revenue_last_four_years,
            "inventory_turnover": self.get_inventory_turnover_last_four_years,
            "quick_ratio": self.get_quick_ratio_last_four_years,
            "receivables_turnover": self.get_receivables_turnover_last_four_years,
            "asset_turnover": self.get_asset_turnover_last_four_years, # asset turnover
            "payables_turnover": self.get_accounts_payable_turnover_last_four_years,
            "fixed_asset_turnover": self.get_fixed_asset_turnover_last_four_years,
            "capex_to_operating_cash_flow": self.get_capex_to_operating_cash_flow_last_four_years,
            "capex_to_operating_income": self.get_capex_to_operating_income_last_four_years,
            "capex_to_revenue": self.get_capex_to_revenue_last_four_years,
            "debt_to_asset":self.get_debt_to_asset_last_four_years_last_four_years,
            "debt_to_equity":self.get_debt_to_equity_last_four_years_last_four_years,
            "equity_to_asset": self.get_equity_to_asset_ratio_last_four_years,
            "interest_coverage": self.get_interest_coverage_last_four_years,
            "liabilities_to_assets": self.get_liabilities_to_asset_ratio_last_four_years,
            "sloan_ratio": self.get_sloan_ratio_last_four_years,
            "net_debt_to_ebitda": self.get_netDebtToEBITDA_last_four_years,
            "debt_to_capital_ratio": self.get_debt_to_capital_ratio_last_four_years,
            "long_term_debt_to_capital_ratio": self.get_long_term_debt_to_capital_ratio_last_four_years,
            "debt_service_coverage_ratio": self.get_debt_service_coverage_ratio_last_four_years,
            "short_term_operating_cashflow_coverage_ratio": self.get_shortTermOperatingCashFlowCoverageRatio_last_four_years,
            "operating_cashflow_coverage_ratio": self.get_operating_cashflow_coverage_ratio_last_four_years,
            "gearing":self.get_gearing_last_four_years,
            "dynamic_debt_degree":self.get_dynamic_debt_degree_last_four_years,
            "current_asset_intensity": self.get_current_asset_intensity_last_four_years,
            "non_current_asset_intensity": self.get_non_current_asset_intensity_last_four_years,
            "asset_cover_ratio_one": self.get_asset_cover_ratio_one_last_four_years,
            "asset_cover_ratio_two": self.get_asset_cover_ratio_two_last_four_years,
            "good_will_ratio": self.get_good_will_ratio_last_four_years ,
            "cash_burn_rate": self.get_cash_burn_rate_last_four_years,
            "fscore": self.get_fscore_last_four_years,
            "gf_score": self.get_gf_score_last_four_years,
            "gf_value": self.get_gf_value_last_four_years,
            "graham_number": self.get_graham_number_last_four_years,
            "mscore": self.get_mscore_last_four_years,
            "price_to_gf_value": self.get_price_to_gf_value_last_four_years,
            "rank_balancesheet": self.get_rank_balancesheet_last_four_years,
            "rank_gf_value": self.get_rank_gf_value_last_four_years,
            "rank_growth": self.get_rank_growth_last_four_years,
            "rank_momentum": self.get_rank_momentum_last_four_years,
            "rank_predictability": self.get_rank_predictability_last_four_years,
            "rank_profitability": self.get_rank_profitability_last_four_years,
            "zscore": self.get_zscore_last_four_years,
            "dividend_paid_and_capex_coverage_ratio": self.get_dividend_paid_and_capex_coverage_ratio_last_four_years,
            "ebitda_margin": self.get_ebitda_margin_last_four_years,
            "ebit_margin": self.get_ebit_margin_last_four_years,
            "fcf_margin": self.get_fcf_margin_last_four_years,
            "fcf_yield": self.get_fcf_yield_last_four_years,
            "gross_margin": self.get_gross_margin_last_four_years,
            "gross_profit_to_asset": self.get_gross_profit_to_asset_last_four_years,
            "net_margin": self.get_net_margin_last_four_years,
            "ocf_margin": self.get_ocf_margin_last_four_years,
            "ocf_yield": self.get_ocf_yield_last_four_years,
            "operating_margin": self.get_operating_margin_last_four_years,
            "return_on_tangible_asset": self.get_return_on_tangible_asset_last_four_years,
            "return_on_tangible_equity": self.get_return_on_tangible_equity_last_four_years,
            "roa": self.get_roa_last_four_years,
            "roce": self.get_roce_last_four_years,
            "roe": self.get_roe_last_four_years,
            "roic": self.get_roic_last_four_years,
            "yield": self.get_yield_last_four_years,
            "freeCashFlowToEquity": self.get_freeCashFlowToEquity_last_four_years,
            "free_cashflow_operating_cashflow_ratio": self.get_free_cashflow_operating_cashflow_ratio_last_four_years,
            "revenue_per_employee":self.get_revenue_per_employee_last_four_years,
            "roi": self.get_roi_last_four_years,
            "capital_turnover": self.get_capital_turnover_last_four_years,
            "cash_per_share": self.get_cash_per_share_last_four_years,
            "ebitda_per_share": self.get_ebitda_per_share_last_four_years,
            "enterprise_value_to_ebit": self.get_enterprise_value_to_ebit_last_four_years,
            "enterprise_value_to_ebitda": self.get_enterprise_value_to_ebitda_last_four_years,
            "enterprise_value_to_fcf": self.get_enterprise_value_to_fcf_last_four_years,
            "enterprise_value_to_ocf": self.get_enterprise_value_to_ocf_last_four_years,
            "enterprise_value_to_revenue": self.get_enterprise_value_to_revenue_last_four_years,
            "free_cash_flow_per_share": self.get_free_cash_flow_per_share_last_four_years,
            "growth_per_share_ebitda": self.get_growth_per_share_ebitda_last_four_years,
            "growth_per_share_eps": self.get_growth_per_share_eps_last_four_years,
            "growth_revenue_per_share": self.get_growth_revenue_per_share_last_four_years,
            "net_cash_per_share": self.get_net_cash_per_share_last_four_years,
            "pb_ratio": self.get_pb_ratio_last_four_years,
            "pe_ratio": self.get_pe_ratio_last_four_years,
            "peg_ratio": self.get_peg_ratio_last_four_years,
            "peter_lynch_fair_value": self.get_peter_lynch_fair_value_last_four_years,
            "price_to_free_cash_flow": self.get_price_to_free_cash_flow_last_four_years,
            "price_to_operating_cash_flow": self.get_price_to_operating_cash_flow_last_four_years,
            "price_to_owner_earnings": self.get_price_to_owner_earnings_last_four_years,
            "price_to_tangible_book": self.get_price_to_tangible_book_last_four_years,
            "ps_ratio": self.get_ps_ratio_last_four_years,
            "revenue_per_share": self.get_revenue_per_share_last_four_years,
            "degree_of_financial_leverage": self.get_degree_of_financial_leverage_last_four_years,
            "degree_of_operating_leverage": self.get_degree_of_operating_leverage_last_four_years,
            "capex_to_depreciation": self.get_capex_to_depreciation_last_four_years,
            "intangibles_to_total_assets": self.get_intangiblesToTotalAssets_last_four_years,
            "financial_leverage_ratio": self.get_financial_leverage_ratio_last_four_years,
            "wacc": self.get_wacc_last_four_years,
            "income_before_tax_profit_margin": self.get_income_before_tax_profit_margin_last_four_years,
            "effective_tax_rate": self.get_effective_tax_rate_last_four_years,
            "income_quality_ratio": self.get_income_quality_ratio_last_four_years
        }
        return metric_handlers

    async def get_calculated_financial_metric_map(self):
        calculated_financial_metric_map = {}
        financial_metrics_to_calculate = await self.get_calculated_financial_metrics()

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
        #return self.total_financial_metric_map.get("cost_of_goods_sold_to_revenue", [])
        cost_of_goods_sold_last_four_years = self.total_financial_metric_map.get("Cost of Goods Sold", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        cost_of_goods_sold_last_to_revenue_last_four_years = []

        for cost_of_goods_sold, revenue in zip(cost_of_goods_sold_last_four_years, revenue_last_four_years):
            cost_of_goods_sold_last_to_revenue_last_four_years.append(round(float(cost_of_goods_sold)/ float(revenue), 2))

        return cost_of_goods_sold_last_four_years



    def get_sales_and_administrative_to_revenue_last_four_years(self):
        sell_and_admin_expenses_last_four_years = self.total_financial_metric_map.get("Selling, General and Administrative Expenses", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        sales_and_administrative_to_revenue_last_four_years = []

        for sell_and_admin_expenses, revenue in zip(sell_and_admin_expenses_last_four_years, revenue_last_four_years):
            sales_and_administrative_to_revenue_last_four_years.append(round(float(sell_and_admin_expenses) / float(revenue), 2))

        return sales_and_administrative_to_revenue_last_four_years


    def get_cost_of_revenue_to_revenue_last_four_years(self):
        cost_of_revenue_last_four_years = self.total_financial_metric_map.get("Reconciled Cost of Revenue", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        cost_of_revenue_to_revenue_last_four_years = []

        for cost_of_revenue, revenue in zip(cost_of_revenue_last_four_years,revenue_last_four_years):
            cost_of_revenue_to_revenue_last_four_years.append(round(float(cost_of_revenue) / float(revenue), 2))

        return cost_of_revenue_to_revenue_last_four_years


    def get_research_and_development_to_revenue_last_four_years(self):
        research_development_expense_last_four_years = self.total_financial_metric_map.get("Research and Development Expenses", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        r_and_d_to_revenue_last_four_years = []

        for r_and_d, revenue in zip(research_development_expense_last_four_years, revenue_last_four_years):
            r_and_d_to_revenue_last_four_years.append(round(float(r_and_d) / float(revenue), 2))

        return r_and_d_to_revenue_last_four_years


    def get_cash_conversion_cycle_last_four_years(self):
        return self.total_financial_metric_map.get("cash_conversion_cycle", [])

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

    def get_defensive_interval_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("defensive_interval_ratio", [])

    def get_inventory_to_revenue_last_four_years(self):
        inventory_last_four_years = self.total_financial_metric_map.get("Inventory", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        inventory_to_revenue_last_four_years = []

        for inventory,revenue in zip(inventory_last_four_years, revenue_last_four_years):
            inventory_to_revenue_last_four_years.append(round(float(inventory)/ float(revenue),2))

        return inventory_to_revenue_last_four_years

    def get_inventory_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("inventory_turnover", [])

    def get_quick_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("quick_ratio", [])

    def get_receivables_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("receivables_turnover", [])

    def get_asset_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("asset_turnover", [])

    def get_accounts_payable_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("payables_turnover", [])

    def get_fixed_asset_turnover_last_four_years(self):
        return self.total_financial_metric_map.get("fixed_asset_turnover", [])

    def get_capex_to_operating_cash_flow_last_four_years(self):
        capex_last_four_years = self.total_financial_metric_map.get("Capital Expenditure", [])
        operative_cashflow_last_four_years = self.total_financial_metric_map.get("Operating Cash Flow", [])

        capex_to_operating_cash_flow_last_four_years = []

        for capex, revenue in zip(capex_last_four_years, operative_cashflow_last_four_years):
            capex_to_operating_cash_flow_last_four_years.append(round(float(capex) / float(revenue),2))

        return capex_to_operating_cash_flow_last_four_years

    def get_capex_to_operating_income_last_four_years(self):

        capex_last_four_years = self.total_financial_metric_map.get("Capital Expenditure", [])
        operating_income_last_four_years = self.total_financial_metric_map.get("Operating Income", [])

        capex_to_operating_income_last_four_years = []

        for capex, revenue in zip(capex_last_four_years, operating_income_last_four_years):
            capex_to_operating_income_last_four_years.append(round(float(capex) / float(revenue), 2))

        return capex_to_operating_income_last_four_years

    def get_capex_to_revenue_last_four_years(self):
        capex_last_four_years = self.total_financial_metric_map.get("Capital Expenditure", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        capex_to_revenue_last_four_years = []

        for capex, revenue in zip(capex_last_four_years, revenue_last_four_years):
            capex_to_revenue_last_four_years.append(round(float(capex) / float(revenue), 2))

        return capex_to_revenue_last_four_years

    def get_debt_to_asset_last_four_years_last_four_years(self):

        #return self.debt_to_metric_ratio_last_four_years("totalAssets")
        return self.total_financial_metric_map.get("debt_to_asset", [])

    def get_debt_to_equity_last_four_years_last_four_years(self):
        #return self.debt_to_metric_ratio_last_four_years("totalShareholderEquity")
        return self.total_financial_metric_map.get("debt_to_equity", [])

    def get_equity_to_asset_ratio_last_four_years(self):

        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])
        asset_last_four_years = self.total_financial_metric_map.get("Total Assets", [])

        equity_to_asset_last_four_years = []

        for equity, assets in zip(equity_last_four_years, asset_last_four_years):
                    equity_to_asset_last_four_years.append(round(float(equity)/float(assets), 4))
        return equity_to_asset_last_four_years

    def get_interest_coverage_last_four_years(self):
        return self.total_financial_metric_map.get("interest_coverage", [])

    def get_liabilities_to_asset_ratio_last_four_years(self):
        liabilities_last_four_years = self.total_financial_metric_map.get("total_liabilities", [])
        asset_last_four_years = self.total_financial_metric_map.get("total_assets", [])

        liabilities_to_asset_ratio_last_four_years = []

        for liability, asset in zip(liabilities_last_four_years, asset_last_four_years):
            liabilities_to_asset_ratio_last_four_years.append(round(float(liability) / float(asset), 2))

        return liabilities_to_asset_ratio_last_four_years
        #return self.get_value_to_asset_ratio_last_four_years("totalLiabilities")


    def get_sloan_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("sloan_ratio", [])

    def get_netDebtToEBITDA_last_four_years(self):
        return self.total_financial_metric_map.get("net_debt_to_ebitda", [])

    def get_debt_to_capital_ratio_last_four_years(self):
        debt_last_four_years = self.total_financial_metric_map.get("Total Debt", [])
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])

        debt_to_capital_ratio_last_four_years = []

        for idx, equity in enumerate(equity_last_four_years):
            current_debt = debt_last_four_years[idx]
            debt_to_capital_ratio_last_four_years.append(round(float(current_debt)/(float(equity)+ float(current_debt)), 2))

        return debt_to_capital_ratio_last_four_years

    def get_long_term_debt_to_capital_ratio_last_four_years(self):
        long_term_debt_last_four_years = self.total_financial_metric_map.get("Long Term Debt and Capital Lease Obligation", [])
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])

        long_debt_to_capital_ratio_last_four_years = []

        for idx, equity in enumerate(equity_last_four_years):
            current_debt = long_term_debt_last_four_years[idx]
            long_debt_to_capital_ratio_last_four_years.append(
                round(float(current_debt) / (float(equity) + float(current_debt)), 2))

        return long_debt_to_capital_ratio_last_four_years

    def get_debt_service_coverage_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("debt_service_coverage_ratio", [])


    def get_shortTermOperatingCashFlowCoverageRatio_last_four_years(self):
        operating_cash_flow_last_four_years = self.total_financial_metric_map.get("operatingCashflow", [])
        current_liabilities_last_four_years = self.total_financial_metric_map.get("totalCurrentLiabilities", [])

        shortTermOperatingCashFlowCoverageRatio_last_four_years = []

        for ope_cashflow, current_liability in zip(operating_cash_flow_last_four_years,current_liabilities_last_four_years):
            shortTermOperatingCashFlowCoverageRatio_last_four_years.append(round(float(ope_cashflow) / float(current_liability), 2))

        return shortTermOperatingCashFlowCoverageRatio_last_four_years


    def get_operating_cashflow_coverage_ratio_last_four_years(self):
        operative_cashflow_last_four_years = self.total_financial_metric_map.get("Operating Cash Flow", [])
        debt_last_four_years = self.total_financial_metric_map.get("Total Debt", [])

        operative_cashflow_coverage_ratio_last_four_years = []

        for operative_cashflow, debt in zip(operative_cashflow_last_four_years, debt_last_four_years):
            operative_cashflow_coverage_ratio_last_four_years.append(round(float(operative_cashflow) / float(debt), 2))

        return operative_cashflow_coverage_ratio_last_four_years

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
        debts = self.total_financial_metric_map.get("Total Debt", [])
        values = self.total_financial_metric_map.get("Total Equity", [])

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


    def get_gearing_last_four_years(self):
        total_liabilities_last_four_years = self.total_financial_metric_map.get("Total Liabilities", [])
        cash_and_equivalents_last_four_years = self.total_financial_metric_map.get("Cash and Cash Equivalents", [])
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])

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
        total_liabilities_last_four_years = self.total_financial_metric_map.get("Total Liabilities", [])
        cash_and_equivalents_last_four_years = self.total_financial_metric_map.get("Cash and Cash Equivalents", [])
        total_free_cash_flow_last_four_years = self.total_financial_metric_map.get("Free Cash Flow", [])

        dynamic_debt_degree_last_four_years = []

        for idx, val in enumerate(total_liabilities_last_four_years):
            current_liability = float(val)
            current_cash_and_equivalents = float(cash_and_equivalents_last_four_years[idx])
            current_total_free_cash = float(total_free_cash_flow_last_four_years[idx])
            val_float = current_liability - current_cash_and_equivalents
            ratio = round(val_float / current_total_free_cash, 2) if current_total_free_cash != 0 else None
            dynamic_debt_degree_last_four_years.append(ratio)
        return dynamic_debt_degree_last_four_years


    def get_current_asset_intensity_last_four_years(self):
        total_assets_last_four_years = self.total_financial_metric_map.get("Total Assets", [])
        total_current_asset_last_four_years = self.total_financial_metric_map.get("Total Current Assets", [])

        current_asset_intensity_last_four_years = []

        for current_asset, total_asset in zip(total_current_asset_last_four_years, total_assets_last_four_years):
            current_asset_intensity_last_four_years.append(round(current_asset / total_asset, 2))

        return current_asset_intensity_last_four_years


    def get_non_current_asset_intensity_last_four_years(self):
        total_assets_last_four_years = self.total_financial_metric_map.get("Total Assets", [])
        total_current_asset_last_four_years = self.total_financial_metric_map.get("Total Current Assets", [])

        non_current_asset_intensity_last_four_years = []

        for idx, current_asset in enumerate(total_current_asset_last_four_years):
            total_asset = float(total_assets_last_four_years[idx])
            non_current_asset = float(total_asset) - float(current_asset)
            non_current_asset_intensity_last_four_years.append(round(float(non_current_asset) / float(total_asset), 2))

        return non_current_asset_intensity_last_four_years

    def get_asset_cover_ratio_one_last_four_years(self):
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])
        asset_last_four_years = self.total_financial_metric_map.get("Total Assets", [])

        asset_coverage_degree_last_four_years = []

        for current_equity, total_asset in zip(equity_last_four_years, asset_last_four_years):
            asset_coverage_degree_last_four_years.append(round(current_equity / total_asset, 2))

        return asset_coverage_degree_last_four_years

    def get_asset_cover_ratio_two_last_four_years(self):
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])
        asset_last_four_years = self.total_financial_metric_map.get("Total Assets", [])
        total_non_current_liabilities_last_four_years = self.total_financial_metric_map.get("Total Non Current Liabilities", [])

        asset_coverage_degree_two_last_four_years = []

        for idx, equity in enumerate(equity_last_four_years):
            non_current_current_liabilities = float(total_non_current_liabilities_last_four_years[idx])
            current_equity = equity
            current_total_asset = float(asset_last_four_years[idx])
            val_float = current_equity + non_current_current_liabilities
            ratio = round(val_float / current_total_asset, 2) if current_total_asset != 0 else None
            asset_coverage_degree_two_last_four_years.append(ratio)
        return asset_coverage_degree_two_last_four_years

    def get_good_will_ratio_last_four_years(self):
        good_will_last_four_years = self.total_financial_metric_map.get("Goodwill", [])
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])
        good_will_ratio_last_four_years = []

        for good_will, equity in zip(good_will_last_four_years, equity_last_four_years):
            good_will_ratio_last_four_years.append(round(float(good_will) / float(equity), 2))

        return good_will_ratio_last_four_years

    def get_cash_burn_rate_last_four_years(self):
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])
        net_income_last_four_years = self.total_financial_metric_map.get("Net Income", []) # net loss ?
        cash_burn_rate_last_four_years = []

        for equity, net_income in zip(equity_last_four_years, net_income_last_four_years):
            cash_burn_rate_last_four_years.append(round(float(equity) / abs(float(net_income)), 2))

        return cash_burn_rate_last_four_years

    def get_fscore_last_four_years(self):
        return self.total_financial_metric_map.get("fscore", [])

    def get_gf_score_last_four_years(self):
        return self.total_financial_metric_map.get("gf_score", [])

    def get_gf_value_last_four_years(self):
        return self.total_financial_metric_map.get("gf_value", [])

    def get_graham_number_last_four_years(self):
        return self.total_financial_metric_map.get("graham_number", [])

    def get_mscore_last_four_years(self):
        return self.total_financial_metric_map.get("mscore", [])

    def get_price_to_gf_value_last_four_years(self):
        return self.total_financial_metric_map.get("price_to_gf_value", [])

    def get_rank_balancesheet_last_four_years(self):
        return self.total_financial_metric_map.get("rank_balancesheet", [])

    def get_rank_gf_value_last_four_years(self):
        return self.total_financial_metric_map.get("rank_gf_value", [])

    def get_rank_growth_last_four_years(self):
        return self.total_financial_metric_map.get("rank_growth", [])

    def get_rank_momentum_last_four_years(self):
        return self.total_financial_metric_map.get("rank_momentum", [])

    def get_rank_predictability_last_four_years(self):
        return self.total_financial_metric_map.get("rank_predictability", [])

    def get_rank_profitability_last_four_years(self):
        return self.total_financial_metric_map.get("rank_profitability", [])

    def get_zscore_last_four_years(self):
        return self.total_financial_metric_map.get("zscore", [])

    def get_dividend_paid_and_capex_coverage_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("dividend_paid_and_capex_coverage_ratio", [])

    def get_ebitda_margin_last_four_years(self):
        ebitda_last_four_years = self.total_financial_metric_map.get("EBITDA", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        ebitda_margin_last_four_years = []

        for ebitda, revenue in zip(ebitda_last_four_years, revenue_last_four_years):
            ebitda_margin_last_four_years.append(round(float(ebitda) / float(revenue), 2))

        return ebitda_margin_last_four_years

    def get_ebit_margin_last_four_years(self):
        return self.total_financial_metric_map.get("ebit_margin", [])

    def get_fcf_margin_last_four_years(self):
        free_cash_flow_last_four_years = self.total_financial_metric_map.get("Free Cash Flow", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        free_cashflow_margin_last_four_years = []
        for free_cash_flow, revenue in zip(free_cash_flow_last_four_years, revenue_last_four_years):
            free_cashflow_margin_last_four_years.append(round(float(free_cash_flow)/float(revenue), 2))

        return free_cashflow_margin_last_four_years

    def get_fcf_yield_last_four_years(self):
        return self.total_financial_metric_map.get("fcf_yield", [])

    def get_gross_margin_last_four_years(self):
        return self.total_financial_metric_map.get("gross_margin", [])

    def get_gross_profit_to_asset_last_four_years(self):
        gross_profit_last_four_years = self.total_financial_metric_map.get("Gross Profit", [])
        asset_last_four_years = self.total_financial_metric_map.get("Total Assets", [])

        gross_profit_to_asset_last_four_years = []

        for gross_profit, asset in zip(gross_profit_last_four_years, asset_last_four_years):
            gross_profit_to_asset_last_four_years.append(round(float(gross_profit)/ float(asset), 2))


        return gross_profit_to_asset_last_four_years


    def get_net_margin_last_four_years(self):
        return self.total_financial_metric_map.get("net_margin", [])

    def get_ocf_margin_last_four_years(self):
        #return self.total_financial_metric_map.get("ocf_margin", [])
        operative_cash_flow_last_four_years = self.total_financial_metric_map.get("Operating Cash Flow", [])
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])

        operating_cash_flow_margin_last_four_years = []

        for operating_cash_flow, revenue in zip(operative_cash_flow_last_four_years, revenue_last_four_years):
            operating_cash_flow_margin_last_four_years.append(round(float(operating_cash_flow)/float(revenue), 2))


        return operating_cash_flow_margin_last_four_years

    def get_ocf_yield_last_four_years(self):
        return self.total_financial_metric_map.get("ocf_yield", [])

    def get_operating_margin_last_four_years(self):
        return self.total_financial_metric_map.get("operating_margin", [])

    def get_return_on_tangible_asset_last_four_years(self):
        return self.total_financial_metric_map.get("return_on_tangible_asset", [])

    def get_return_on_tangible_equity_last_four_years(self):
        return self.total_financial_metric_map.get("return_on_tangible_equity", [])

    def get_roa_last_four_years(self):
        return self.total_financial_metric_map.get("roa", [])

    def get_roce_last_four_years(self):
        return self.total_financial_metric_map.get("roce", [])

    def get_roe_last_four_years(self):
        return self.total_financial_metric_map.get("roe", [])

    def get_roic_last_four_years(self):
        return self.total_financial_metric_map.get("roic", [])

    def get_yield_last_four_years(self):
        return self.total_financial_metric_map.get("yield", [])

    def get_freeCashFlowToEquity_last_four_years(self):
        free_cash_flow_last_four_years = self.total_financial_metric_map.get("Free Cash Flow", [])
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])

        free_cash_flow_to_equity_last_four_years = []

        for free_cash_flow, equity in zip(free_cash_flow_last_four_years, equity_last_four_years):
            free_cash_flow_to_equity_last_four_years.append(round(float(free_cash_flow) / float(equity), 2))

        return free_cash_flow_last_four_years

    def get_free_cashflow_operating_cashflow_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("free_cashflow_operating_cashflow_ratio", [])

    def get_revenue_per_employee_last_four_years(self):
        revenue_last_four_years = self.total_financial_metric_map.get("revenue", [])
        employee_amount_last_four_years = self.total_financial_metric_map.get("total_employee_number", [])

        revenue_per_employee_last_four_years = []

        for revenue, employee_amount in zip(revenue_last_four_years, employee_amount_last_four_years):
            revenue_per_employee_last_four_years.append(round(float(revenue) / float(employee_amount), 2))
        return revenue_per_employee_last_four_years

    def get_roi_last_four_years(self):
        operating_income_last_four_years = self.total_financial_metric_map.get("Operating Income", [])
        total_assets_last_four_years = self.total_financial_metric_map.get("Total Assets", [])

        roi_last_four_years = []

        for operating_income, total_asset in zip(operating_income_last_four_years,total_assets_last_four_years):
            roi_last_four_years.append(round(float(operating_income) / float(total_asset), 2))

        return roi_last_four_years

    def get_capital_turnover_last_four_years(self):
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])
        total_assets_last_four_years = self.total_financial_metric_map.get("Total Assets", [])

        capital_turnover_last_four_years = []

        for revenue,total_asset in zip(revenue_last_four_years, total_assets_last_four_years):
            capital_turnover_last_four_years.append(round(float(revenue) / float(total_asset), 2))

        return capital_turnover_last_four_years

    def get_cash_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("cash_per_share", [])

    def get_ebitda_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("ebitda_per_share", [])

    def get_enterprise_value_to_ebit_last_four_years(self):
        return self.total_financial_metric_map.get("enterprise_value_to_ebit", [])

    def get_enterprise_value_to_ebitda_last_four_years(self):
        return self.total_financial_metric_map.get("enterprise_value_to_ebitda", [])

    def get_enterprise_value_to_fcf_last_four_years(self):
        return self.total_financial_metric_map.get("enterprise_value_to_fcf", [])

    def get_enterprise_value_to_ocf_last_four_years(self):
        return self.total_financial_metric_map.get("enterprise_value_to_ocf", [])

    def get_enterprise_value_to_revenue_last_four_years(self):
        return self.total_financial_metric_map.get("enterprise_value_to_revenue", [])

    def get_free_cash_flow_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("free_cash_flow_per_share", [])

    def get_growth_per_share_ebitda_last_four_years(self):
        return self.total_financial_metric_map.get("growth_per_share_ebitda", [])

    def get_growth_per_share_eps_last_four_years(self):
        return self.total_financial_metric_map.get("growth_per_share_eps", [])

    def get_growth_revenue_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("growth_revenue_per_share", [])

    def get_net_cash_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("net_cash_per_share", [])

    def get_pb_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("pb_ratio", [])

    def get_pe_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("pe_ratio", [])

    def get_peg_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("peg_ratio", [])

    def get_peter_lynch_fair_value_last_four_years(self):
        return self.total_financial_metric_map.get("peter_lynch_fair_value", [])

    def get_price_to_free_cash_flow_last_four_years(self):
        return self.total_financial_metric_map.get("price_to_free_cash_flow", [])

    def get_price_to_operating_cash_flow_last_four_years(self):
        return self.total_financial_metric_map.get("price_to_operating_cash_flow", [])

    def get_price_to_owner_earnings_last_four_years(self):
        return self.total_financial_metric_map.get("price_to_owner_earnings", [])

    def get_price_to_tangible_book_last_four_years(self):
        return self.total_financial_metric_map.get("price_to_tangible_book", [])

    def get_ps_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("ps_ratio", [])

    def get_revenue_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("revenue_per_share", [])

    def get_degree_of_financial_leverage_last_four_years(self):
        return self.total_financial_metric_map.get("degree_of_financial_leverage", [])

    def get_degree_of_operating_leverage_last_four_years(self):
        return self.total_financial_metric_map.get("degree_of_operating_leverage", [])

    def get_capex_to_depreciation_last_four_years(self):
        capex_last_four_years = self.total_financial_metric_map.get("Capital Expenditure", [])
        depreciation_last_four_years = self.total_financial_metric_map.get("Accumulated Depreciation", [])

        capex_to_depreciation_last_four_years = []

        for capex, depreciation in zip(capex_last_four_years, depreciation_last_four_years):
            capex_to_depreciation_last_four_years.append(round(float(capex)/float(depreciation),2))

        return capex_to_depreciation_last_four_years


    def get_intangiblesToTotalAssets_last_four_years(self):
        intangibles_last_four_years = self.total_financial_metric_map.get("Intangible Assets", [])
        total_assets_last_four_years = self.total_financial_metric_map.get("Total Assets", [])

        intangibles_to_assets_last_four_years = []

        for intangible, asset in zip(intangibles_last_four_years, total_assets_last_four_years):
            intangibles_to_assets_last_four_years.append(round(float(intangible) / float(asset), 2))

        return intangibles_to_assets_last_four_years

    def get_financial_leverage_ratio_last_four_years(self):
        liabilities_last_four_years = self.total_financial_metric_map.get("Total Liabilities", [])
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])

        financial_leverage_ratio_last_four_years = []

        for liability, equity in zip(liabilities_last_four_years, equity_last_four_years):
            financial_leverage_ratio_last_four_years.append(round(float(liability) / float(equity), 2))

        return financial_leverage_ratio_last_four_years

    def get_wacc_last_four_years(self):
        return self.total_financial_metric_map.get("wacc", [])

    def get_income_before_tax_profit_margin_last_four_years(self):
        return self.total_financial_metric_map.get("income_before_tax_profit_margin", [])

    def get_effective_tax_rate_last_four_years(self):
        return self.total_financial_metric_map.get("effective_tax_rate", [])

    def get_income_quality_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("income_quality_ratio", [])
