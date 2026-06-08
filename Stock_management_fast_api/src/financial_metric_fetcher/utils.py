def get_alpha_ventage_metrics() -> list[str]:
    return [

    ]


def get_fmp_metrics() -> list[str]:
    return [
        "costOfRevenue"
    ]


def get_guro_metrics() -> list[str]:
    return [
        "degree_of_financial_leverage",
        "degree_of_operating_leverage",
        "enterprise_value_to_fcf",
        "fscore",
        "gf_score",
        "gf_value",
        "graham_number",
        "price_to_gf_value",
        "mscore",
        "ocf_yield",
        "yield",
        "peter_lynch_fair_value",
        "ps_ratio",
        "rank_balancesheet",
        "rank_gf_value",
        "rank_growth",
        "rank_momentum",
        "rank_predictability",
        "rank_profitability",
        "return_on_tangible_equity",
        "shiller_pe_ratio",
        "sloan_ratio",
        "snoa",
        "total_employee_number",
        "turnover",
        "wacc",
        "cash_per_share",
        "ebitda_per_share",
        "free_cash_flow_per_share",
        "growth_per_share_ebitda",
        "growth_per_share_eps",
        "net_cash_per_share",
        "price_to_operating_cash_flow",
        "price_to_owner_earnings",
        "price_to_tangible_book",
        "defensive_interval_ratio"
    ]

def get_considered_financial_metric_of_pip_sources() -> list[str]:
    return [
        "Gross Margin",
        "Operating Margin",
        "Net Profit Margin",
        "Interest Coverage Ratio",
        "Income Before Tax Profit Margin",
        "Effective Tax Rate",
        "Return on Assets",
        "Return on Equity",
        "Return on Invested Capital",
        "Return on Capital Employed",
        "Return on Tangible Assets"
        "Income Quality Ratio",
        "Free Cash Flow to Operating Cash Flow Ratio",
        "EBIT to Revenue",
        "Days of Inventory Outstanding",
        "Days of Sales Outstanding",
        "Operating Cycle",
        "Days of Accounts Payable Outstanding",
        "Cash Conversion Cycle",
        "Cash Conversion Efficiency",
        "Receivables Turnover",
        "Inventory Turnover Ratio",
        "Accounts Payable Turnover Ratio",
        "SGA-to-Revenue Ratio",
        "Fixed Asset Turnover",
        "Asset Turnover Ratio",
        "Operating Ratio",
        "Current Ratio",
        "Quick Ratio",
        "Cash Ratio",
        "Working Capital",
        "Operating Cash Flow Ratio",
        "Operating Cash Flow to Sales Ratio",
        "Short Term Coverage Ratio",
        "Debt-to-Assets Ratio",
        "Debt-to-Equity Ratio",
        "Debt Service Coverage Ratio",
        "Free Cash Flow Yield",
        "Net-Debt to EBITDA Ratio",
        "Cash Flow Coverage Ratio",
        "Dividend CAPEX Coverage Ratio",
        "Earnings per Share",
        "Revenue per Share",
        "Price-to-Earnings",
        "Price-to-Earnings-Growth",
        "Book Value per Share",
        "Price-to-Book",
        "Price-to-Cash-Flow",
        "Price-to-Free-Cash-Flow",
        "EV-to-Sales",
        "EV-to-EBIT",
        "EV-to-EBITDA",
        "EV-to-Operating-Cash-Flow",
        "Piotroski Score",
        "Altman Z-Score",
    ]

def get_considered_raw_metrics() -> list[str]:
    return [
        "Goodwill",
        "Total Equity",
        "Operating Income"
        "Total Debt"
        "EBITDA",
        "Revenue",
        "Free Cash Flow",
        "Operating Cash Flow",
        "Cash and Cash Equivalents",
        "Total Liabilities",
        "Total Assets",
        "Total Non Current Liabilities",
        "Total Current Assets",
        "Gross Profit",
        "Inventory",
        "Intangible Assets",
        "Capital Expenditure",
        "Cost of Goods Sold",
        "Long Term Debt and Capital Lease Obligation",
        "Accumulated Depreciation",
        "Net Income"
    ]

def metric_will_be_considered(metric: str, financial_metrics_to_consider:list[str]) -> bool:
    return metric in financial_metrics_to_consider

def merge_all_financial_metrics_map(*maps: dict) -> dict:
    result = {}
    for m in maps:
        for k, v in m.items():
            result.setdefault(k, v)
    return result

