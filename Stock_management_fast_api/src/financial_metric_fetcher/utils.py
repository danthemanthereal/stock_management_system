def get_alpha_ventage_metrics()-> list[str]:
    return [
        "costOfRevenue"
    ]

def get_fmp_metrics()-> list[str]:
    return [
        "costOfRevenue"
    ]

def get_guro_metrics()-> list[str]:
    return [
        "capex_to_operating_cash_flow",
        "capex_to_operating_income",
        "capex_to_revenue",
        "cash_ratio",
        "cost_of_goods_sold_to_revenue",
        "current_ratio",
        "days_inventory",
        "days_payable",
        "days_sales_outstanding",
        "debt_to_asset",
        "debt_to_equity",
        "degree_of_financial_leverage",
        "degree_of_operating_leverage",
        "ebitda_margin",
        "enterprise_value_to_ebit",
        "enterprise_value_to_ebitda",
        "enterprise_value_to_fcf",
        "enterprise_value_to_ocf",
        "enterprise_value_to_revenue",
        "equity_to_asset",
        "fcf_margin",
        "fcf_yield",
        "fscore",
        "gf_score",
        "gf_value",
        "graham_number",
        "gross_margin",
        "gross_profit_to_asset",
        "inventory_to_revenue",
        "inventory_turnover",
        "net_margin",
        "ocf_margin",
        "ocf_yield",
        "operating_margin",
        "pb_ratio",
        "pe_ratio",
        "peg_ratio",
        "peter_lynch_fair_value",
        "ps_ratio",
        "quick_ratio",
        "rank_balancesheet",
        "rank_gf_value",
        "rank_growth",
        "rank_momentum",
        "rank_predictability",
        "rank_profitability",
        "rd2rev",
        "receivables_turnover",
        "return_on_tangible_asset",
        "return_on_tangible_equity",
        "roa",
        "roce",
        "roe",
        "roic",
        "shiller_pe_ratio",
        "sloan_ratio",
        "snoa",
        "total_employee_number",
        "turnover",
        "wacc",
        "zscore"
    ]





def merge_all_financial_metrics_map(*maps: dict) -> dict:
    result = {}
    for m in maps:
        for k, v in m.items():
            result.setdefault(k, v)
    return result