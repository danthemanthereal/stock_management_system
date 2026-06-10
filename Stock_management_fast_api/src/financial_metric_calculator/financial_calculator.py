from sqlalchemy.ext.asyncio import AsyncSession
from functools import partial

class FinancialMetricCalculator:
    def __init__(self, total_financial_metric_map, db: AsyncSession):
        self.total_financial_metric_map = total_financial_metric_map
        self.db = db
        self.financial_metrics_handler = self.init_financial_metrics_handler()


    def init_financial_metrics_handler(self):
        metric_handlers = {

            "cost_of_goods_and_service_sold_to_revenue": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Cost of Goods Sold", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "sales_general_and_administrative_to_revenue": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Selling, General and Administrative Expenses", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "cost_of_revenue_to_revenue":partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Reconciled Cost of Revenue", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "research_and_developement_to_revenue": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Research and Development Expenses", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "cash_conversion_cycle": partial(self.get_financial_metric_direct_by_map, "cash_conversion_cycle"),
            "cash_ratio": partial(self.get_financial_metric_direct_by_map, "cash_ratio"),
            "current_ratio":partial(self.get_financial_metric_direct_by_map, "current_ratio"),
            "days_inventory": partial(self.get_financial_metric_direct_by_map, "days_inventory"),
            "days_payable": partial(self.get_financial_metric_direct_by_map, "days_payable"),
            "days_sales_outstanding": partial(self.get_financial_metric_direct_by_map, "days_sales_outstanding"),
            "defensive_interval_ratio": partial(self.get_financial_metric_direct_by_map, "defensive_interval_ratio"),
            "inventory_to_revenue": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Inventory", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "inventory_turnover": partial(self.get_financial_metric_direct_by_map, "inventory_turnover"),
            "quick_ratio": partial(self.get_financial_metric_direct_by_map, "quick_ratio"),
            "receivables_turnover": partial(self.get_financial_metric_direct_by_map, "receivables_turnover"),
            "asset_turnover": partial(self.get_financial_metric_direct_by_map, "asset_turnover"),
            "payables_turnover": partial(self.get_financial_metric_direct_by_map, "payables_turnover"),
            "fixed_asset_turnover": partial(self.get_financial_metric_direct_by_map, "fixed_asset_turnover"),
            "capex_to_operating_cash_flow": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Capital Expenditure", []),
                                                                 self.total_financial_metric_map.get("Operating Cash Flow", [])),
            "capex_to_operating_income": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Capital Expenditure", []),
                                                                 self.total_financial_metric_map.get("Operating Income", [])),
            "capex_to_revenue": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Capital Expenditure", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "debt_to_asset":partial(self.get_financial_metric_direct_by_map, "debt_to_asset"),
            "debt_to_equity":partial(self.get_financial_metric_direct_by_map, "debt_to_equity"),
            "equity_to_asset": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Total Equity", []),
                                                                 self.total_financial_metric_map.get("Total Assets", [])),
            "interest_coverage": partial(self.get_financial_metric_direct_by_map, "interest_coverage"),
            "liabilities_to_assets": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Total Liabilities", []),
                                                                 self.total_financial_metric_map.get("Total Assets", [])),
            "sloan_ratio": partial(self.get_financial_metric_direct_by_map, "sloan_ratio"),
            "net_debt_to_ebitda": partial(self.get_financial_metric_direct_by_map, "net_debt_to_ebitda"),
            "debt_to_capital_ratio": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Total Debt", []),
                                                                 self.total_financial_metric_map.get("Total Equity", [])),
            "long_term_debt_to_capital_ratio": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Long Term Debt and Capital Lease Obligation", []),
                                                                 self.total_financial_metric_map.get("Total Equity", [])),
            "debt_service_coverage_ratio": partial(self.get_financial_metric_direct_by_map, "debt_service_coverage_ratio"),
            "short_term_operating_cashflow_coverage_ratio": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Operating Cash Flow", []),
                                                                 self.total_financial_metric_map.get("Total Current Liabilities", [])),
            "operating_cashflow_coverage_ratio": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Operating Cash Flow", []),
                                                                 self.total_financial_metric_map.get("Total Debt", [])),
            "cash_flow_coverage_ratio":partial(self.get_financial_metric_direct_by_map, "cash_flow_coverage_ratio"),
            "gearing":self.get_gearing_last_four_years,
            "dynamic_debt_degree":self.get_dynamic_debt_degree_last_four_years,
            "current_asset_intensity": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Total Current Assets", []),
                                                                 self.total_financial_metric_map.get("Total Assets", [])),
            "non_current_asset_intensity": self.get_non_current_asset_intensity_last_four_years,
            "asset_cover_ratio_one": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Total Equity", []),
                                                                 self.total_financial_metric_map.get("Total Assets", [])),
            "asset_cover_ratio_two": self.get_asset_cover_ratio_two_last_four_years,
            "good_will_ratio": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Goodwill", []),
                                                                 self.total_financial_metric_map.get("Total Equity", [])) ,
            "cash_burn_rate": self.get_cash_burn_rate_last_four_years,
            "fscore": partial(self.get_financial_metric_direct_by_map, "fscore"),
            "gf_score": partial(self.get_financial_metric_direct_by_map, "gf_score"),
            "gf_value": partial(self.get_financial_metric_direct_by_map, "gf_value"),
            "graham_number":  partial(self.get_financial_metric_direct_by_map, "graham_number"),
            "mscore": partial(self.get_financial_metric_direct_by_map, "mscore"),
            "price_to_gf_value": partial(self.get_financial_metric_direct_by_map, "price_to_gf_value"),
            "rank_balancesheet": partial(self.get_financial_metric_direct_by_map, "rank_balancesheet"),
            "rank_gf_value": partial(self.get_financial_metric_direct_by_map, "rank_gf_value"),
            "rank_growth": partial(self.get_financial_metric_direct_by_map, "rank_growth"),
            "rank_momentum": partial(self.get_financial_metric_direct_by_map, "rank_momentum"),
            "rank_predictability": partial(self.get_financial_metric_direct_by_map, "rank_predictability"),
            "rank_profitability": partial(self.get_financial_metric_direct_by_map, "rank_profitability"),
            "zscore": partial(self.get_financial_metric_direct_by_map, "zscore"),
            "dividend_paid_and_capex_coverage_ratio": partial(self.get_financial_metric_direct_by_map, "dividend_paid_and_capex_coverage_ratio"),
            "ebitda_margin": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("EBITDA", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "ebit_margin": partial(self.get_financial_metric_direct_by_map, "ebit_margin"),
            "fcf_margin": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Free Cash Flow", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "fcf_yield": partial(self.get_financial_metric_direct_by_map, "fcf_yield"),
            "gross_margin": partial(self.get_financial_metric_direct_by_map, "gross_margin"),
            "gross_profit_to_asset": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Gross Profit", []),
                                                                 self.total_financial_metric_map.get("Total Assets", [])),
            "net_margin": partial(self.get_financial_metric_direct_by_map, "net_margin"),
            "ocf_margin": partial(self.get_financial_metric_by_calculate_to_raw_date,
                                                                 self.total_financial_metric_map.get("Operating Cash Flow", []),
                                                                 self.total_financial_metric_map.get("Revenue", [])),
            "ocf_yield": partial(self.get_financial_metric_direct_by_map, "ocf_yield"),
            "operating_margin": partial(self.get_financial_metric_direct_by_map, "operating_margin"),
            "return_on_tangible_asset": partial(self.get_financial_metric_direct_by_map, "return_on_tangible_asset"),
            "return_on_tangible_equity": partial(self.get_financial_metric_direct_by_map, "return_on_tangible_equity"),
            "roa": partial(self.get_financial_metric_direct_by_map, "roa"),
            "roce": partial(self.get_financial_metric_direct_by_map, "roce"),
            "roe": partial(self.get_financial_metric_direct_by_map, "roe"),
            "roic": partial(self.get_financial_metric_direct_by_map, "roic"),
            "yield": partial(self.get_financial_metric_direct_by_map, "yield"),
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
            "income_quality_ratio": self.get_income_quality_ratio_last_four_years,
            "operating_cycle":self.get_operating_cycle_last_four_years,
            "cash_conversion_efficiency":self.get_cash_conversion_efficiency_last_four_years,
            "sga_to_revenue": self.get_sga_to_revenue_last_four_years,
            "operating_ratio":self.get_operating_ratio_last_four_years,
            "short_term_coverage_ratio":self.get_short_term_coverage_ratio_last_four_years,
            "earnings_per_share":self.get_earnings_per_share_last_four_years,
            "book_value_per_share":self.get_book_value_per_share_last_four_years,
            "price_to_cashflow":self.get_price_to_cashflow_last_four_years,
            "piotroski": self.get_piotroski_last_four_years,
            "revenue_to_cost":self.get_revenue_to_cost_ratio_last_four_years,
            "gross_profit_to_cost":self.get_gross_profit_to_cost_last_four_years,
            "revenue_per_employee_cost": self.get_revenue_per_employee_cost_ratio_last_four_years
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

    def get_financial_metric_by_calculate_to_raw_date(self, numerator: list, denominator: list ) ->list[float]:
        return [round(float(numer)/float(denom), 2) for numer, denom in zip(numerator, denominator) ]

    def get_financial_metric_direct_by_map(self, financial_metric_name: str):
        return self.total_financial_metric_map.get(financial_metric_name, [])

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

    def get_non_current_asset_intensity_last_four_years(self):
        total_assets_last_four_years = self.total_financial_metric_map.get("Total Assets", [])
        total_current_asset_last_four_years = self.total_financial_metric_map.get("Total Current Assets", [])

        non_current_asset_intensity_last_four_years = []

        for idx, current_asset in enumerate(total_current_asset_last_four_years):
            total_asset = float(total_assets_last_four_years[idx])
            non_current_asset = float(total_asset) - float(current_asset)
            non_current_asset_intensity_last_four_years.append(round(float(non_current_asset) / float(total_asset), 2))

        return non_current_asset_intensity_last_four_years

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

    def get_cash_burn_rate_last_four_years(self):
        equity_last_four_years = self.total_financial_metric_map.get("Total Equity", [])
        net_income_last_four_years = self.total_financial_metric_map.get("Net Income", []) # net loss ?
        cash_burn_rate_last_four_years = []

        for equity, net_income in zip(equity_last_four_years, net_income_last_four_years):
            cash_burn_rate_last_four_years.append(round(float(equity) / abs(float(net_income)), 2))

        return cash_burn_rate_last_four_years


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

    def get_operating_cycle_last_four_years(self):
        return self.total_financial_metric_map.get("operating_cycle", [])

    def get_cash_conversion_efficiency_last_four_years(self):
        return self.total_financial_metric_map.get("cash_conversion_efficiency", [])

    def get_sga_to_revenue_last_four_years(self):
        return self.total_financial_metric_map.get("sga_to_revenue", [])

    def get_operating_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("operating_ratio", [])

    def get_short_term_coverage_ratio_last_four_years(self):
        return self.total_financial_metric_map.get("short_term_coverage_ratio", [])

    def get_earnings_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("earnings_per_share", [])

    def get_book_value_per_share_last_four_years(self):
        return self.total_financial_metric_map.get("book_value_per_share", [])

    def get_price_to_cashflow_last_four_years(self):
        return self.total_financial_metric_map.get("price_to_cashflow", [])

    def get_piotroski_last_four_years(self):
        return self.total_financial_metric_map.get("piotroski", [])

    def get_revenue_to_cost_ratio_last_four_years(self):
        revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])
        cost_and_expenses_last_four_years = self.total_financial_metric_map.get("Cost and Expenses", [])

        revenue_to_cost_ratio_last_four_years = []

        for revenue, cost_and_expenses in zip(revenue_last_four_years, cost_and_expenses_last_four_years):
            revenue_to_cost_ratio_last_four_years.append(round(float(revenue) / float(cost_and_expenses), 2))


        return revenue_to_cost_ratio_last_four_years

    def get_gross_profit_to_cost_last_four_years(self):
        gross_profit_last_four_years = self.total_financial_metric_map.get("Gross Profit", [])
        cost_and_expenses_last_four_years = self.total_financial_metric_map.get("Cost and Expenses", [])

        gross_profit_to_cost_ratio_last_four_years = []

        for gross_profit, cost_and_expenses in zip(gross_profit_last_four_years, cost_and_expenses_last_four_years):
            gross_profit_to_cost_ratio_last_four_years.append(round(float(gross_profit) / float(cost_and_expenses), 2))

        return gross_profit_to_cost_ratio_last_four_years

    def get_revenue_per_employee_cost_ratio_last_four_years(self)->list[float]:
        try:
            revenue_last_four_years = self.total_financial_metric_map.get("Revenue", [])
            r_and_d_last_four_years = self.total_financial_metric_map.get("Research and Development Expenses", [])
            selling_and_admin_last_four_years = self.total_financial_metric_map.get("Selling, General and Administrative Expenses", [])

            revenue_per_employee_cost_ratio_last_four_years = []

            for idx, revenue in enumerate(revenue_last_four_years):
                r_and_d = r_and_d_last_four_years[idx]
                selling_and_admin = selling_and_admin_last_four_years[idx]
                personal_cost = float(r_and_d) + float(selling_and_admin)
                revenue_per_employee_cost_ratio_last_four_years.append(round(float(revenue) / float(personal_cost), 2))

            return revenue_per_employee_cost_ratio_last_four_years

        except Exception as e:
            print(e)
            return []