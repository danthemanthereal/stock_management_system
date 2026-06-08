from src.financial_metric_fetcher.financial_metric_fetcher import FinancialMetricFetcher
from financetoolkit import Toolkit
from dotenv import load_dotenv
import os

from src.financial_metric_fetcher.utils import get_considered_financial_metric_of_pip_sources

load_dotenv()

class FROMPIPInstallSourceFetcher(FinancialMetricFetcher):

    def __init__(self):
        self.metrics_to_consider = get_considered_financial_metric_of_pip_sources()
        self.api_metric_database_mapping =  {
    "Gross Margin": "gross_margin",
    "Operating Margin": "operating_margin",
    "Net Profit Margin": "net_margin",
    "Interest Coverage Ratio": "interest_coverage",
    "Income Before Tax Profit Margin": "income_before_tax_profit_margin",
    "Effective Tax Rate": "effective_tax_rate",
    "Return on Assets": "roa",
    "Return on Equity": "roe",
    "Return on Invested Capital": "roic",
    "Return on Capital Employed": "roce",
    "Return on Tangible Assets": "return_on_tangible_asset",
    "Income Quality Ratio": "income_quality_ratio",
    "Free Cash Flow to Operating Cash Flow Ratio": "free_cashflow_operating_cashflow_ratio",
    "EBIT to Revenue": "ebit_margin",
    "Days of Inventory Outstanding": "days_inventory",
    "Days of Sales Outstanding": "days_sales_outstanding",
    "Operating Cycle": "operating_cycle",
    "Days of Accounts Payable Outstanding": "days_payable",
    "Cash Conversion Cycle": "cash_conversion_cycle",
    "Cash Conversion Efficiency": "cash_conversion_efficiency",
    "Receivables Turnover": "receivables_turnover",
    "Inventory Turnover Ratio": "inventory_turnover",
    "Accounts Payable Turnover Ratio": "payablesTurnover",
    "SGA-to-Revenue Ratio": "sga_to_revenue",
    "Fixed Asset Turnover": "fixed_asset_turnover",
    "Asset Turnover Ratio": "",
    "Operating Ratio": "operating_ratio",
    "Current Ratio": "current_ratio",
    "Quick Ratio": "quick_ratio",
    "Cash Ratio": "cash_ratio",
    "Operating Cash Flow Ratio": "operating_cashflow_ratio",
    "Operating Cash Flow to Sales Ratio": "operating_cashflow_sales_ratio",
    "Short Term Coverage Ratio": "short_term_coverage_ratio",
    "Debt-to-Assets Ratio": "debt_to_asset",
    "Debt-to-Equity Ratio": "debt_to_equity",
    "Debt Service Coverage Ratio": "debt_service_coverage_ratio",
    "Free Cash Flow Yield": "fcf_yield",
    "Net-Debt to EBITDA Ratio": "net_debt_to_ebitda",
    "Cash Flow Coverage Ratio": "cash_flow_coverage_ratio",
    "Dividend CAPEX Coverage Ratio": "dividend_paid_and_capex_coverage_ratio",
    "Earnings per Share": "earnings_per_share",
    "Revenue per Share": "revenue_per_share",
    "Price-to-Earnings": "pe_ratio",
    "Price-to-Earnings-Growth": "peg_ratio",
    "Book Value per Share": "book_value_per_share",
    "Price-to-Book": "pb_ratio",
    "Price-to-Cash-Flow": "price_to_cashflow",
    "Price-to-Free-Cash-Flow": "price_to_free_cash_flow",
    "EV-to-Sales": "enterprise_value_to_revenue",
    "EV-to-EBIT": "enterprise_value_to_ebit",
    "EV-to-EBITDA": "enterprise_value_to_ebitda",
    "EV-to-Operating-Cash-Flow": "enterprise_value_to_ocf",
    "Piotroski Score": "",
    "Altman Z-Score": "zscore"
}

    async def fetch(self, company_ticker: str) -> dict[str, list]:

        metrics_of_company_from_pip_sources = {}

        company = Toolkit(
        tickers=[company_ticker],
        api_key=os.getenv("FMP_API_KEY"),
        )

        metrics_of_company_from_pip_sources = self.insert_metrics_by_type(
            company=company,
            metrics_dict=metrics_of_company_from_pip_sources,
            ratio_type="efficiency"
        )

        metrics_of_company_from_pip_sources = self.insert_metrics_by_type(
            company=company,
            metrics_dict=metrics_of_company_from_pip_sources,
            ratio_type="liquidity"
        )
        metrics_of_company_from_pip_sources = self.insert_metrics_by_type(
            company=company,
            metrics_dict=metrics_of_company_from_pip_sources,
            ratio_type="profitability"
        )

        metrics_of_company_from_pip_sources = self.insert_metrics_by_type(
            company=company,
            metrics_dict=metrics_of_company_from_pip_sources,
            ratio_type="solvency"
        )

        metrics_of_company_from_pip_sources = self.insert_metrics_by_type(
            company=company,
            metrics_dict=metrics_of_company_from_pip_sources,
            ratio_type="valuation"
        )

        return metrics_of_company_from_pip_sources

    def insert_metrics_by_type(self, company: Toolkit, metrics_dict: dict[str, list], ratio_type: str) -> dict[
        str, list]:

        years = ["2022", "2023", "2024", "2025"]
        method_name = f"collect_{ratio_type}_ratios"
        collect_method = getattr(company.ratios, method_name)
        df = collect_method()

        for metric in self.metrics_to_consider:
            if metric in df.index:
                values = df.loc[metric, years].tolist()
                db_key = self.api_metric_database_mapping.get(metric, "")
                metrics_dict[db_key] = values

        return metrics_dict

