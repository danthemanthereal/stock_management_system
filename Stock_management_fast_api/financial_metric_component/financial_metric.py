import requests
from database.models import FinancialMetric
from playwright.async_api import async_playwright
import json
from sqlalchemy import and_


def get_total_financial_metrics(db, company_name: str)->dict:
    total_financial_metric_map = {}
    total_financial_metric_map = get_financial_metrics_by_guro_focus(db, total_financial_metric_map)
    total_financial_metric_map = get_financial_metrics_with_alpha_ventage_api(db, total_financial_metric_map, company_name)
    total_financial_metric_map = get_financial_metrics_with_fmp_api(db, total_financial_metric_map, company_name)
    total_financial_metric_map = get_calculated_metrics(db, total_financial_metric_map, company_name)
    return  total_financial_metric_map

def get_financial_metrics_by_guro_focus(db, financial_metric_map: dict)->dict:
    """async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async with page.expect_response(
                lambda r: "/_api/stocks/" in r.url and "financial" in r.url,
                timeout=60000
        ) as response_info:
            await page.goto(f"https://www.gurufocus.com/stock/{company}/financials")

        response = await response_info.value
        data = await response.json()
        print(f"data {data}")
        await browser.close()
        return data"""

    with open("/Users/danielschmidt/Desktop/stock_management_system/Stock_management_fast_api/financial_metric_component/current_financial_metrics_guro_focus.json") as financial_metrics_file:
        financial_metrics = json.load(financial_metrics_file)


    annuals = financial_metrics.get("annual", [])
    for current_year_map in annuals:
        for key, value in current_year_map.items():
            if key == "date":
                continue
            financial_metric_object = db.query(FinancialMetric).filter(
            and_(
                FinancialMetric.name == key,
                FinancialMetric.is_active == True
            )
            ).first()
            if not financial_metric_object:
                continue
            financial_metric_map.setdefault(key, []).append(value)

    return financial_metric_map


def get_financial_metrics_with_alpha_ventage_api(db, financial_metric_map, company_name):
    alpha_vantage_api_key = "QZX1ZGLLW5C7LMB0"
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={company_name}&apikey={alpha_vantage_api_key}'
    r = requests.get(url)
    financial_metric_to_get = ["costOfRevenue"]
    ## 22, 23, 24, 25
    annual_reports = list(reversed(r.json()['annualReports']))[-4:]
    for annual_report in annual_reports:
        for (key, value) in annual_report.items():
            if key in financial_metric_to_get:
                financial_metric_object = db.query(FinancialMetric).filter(
                    and_(
                        FinancialMetric.name == key,
                        FinancialMetric.is_active == True
                    )
                ).first()
                if not financial_metric_object:
                    continue
                financial_metric_map.setdefault(key, []).append(value)
    return financial_metric_map

def get_financial_metrics_with_fmp_api(db, financial_metric_map, company_name):
    fmp_api_key = "xYWzSku7uTc6MnZk5Qdm4Lrd7WVRVZzr"
    key_metrics_to_consider =[
    "capexToDepreciation",
    "salesGeneralAndAdministrativeToRevenue",
    "researchAndDevelopementToRevenue",
    "intangiblesToTotalAssets",
    "daysOfPayablesOutstanding",
    "daysOfInventoryOutstanding",
    "freeCashFlowToEquity",
    "freeCashFlowToFirm"
    ]

    ratio_metrics_to_consider = [
        "ebitMargin",
        "operatingProfitMargin",
        "pretaxProfitMargin",
        "netProfitMargin",
        "payablesTurnover",
        "fixedAssetTurnover",
        "solvencyRatio",
        "priceToEarningsRatio",
        "priceToEarningsGrowthRatio",
        "forwardPriceToEarningsGrowthRatio",
        "priceToBookRatio",
        "priceToSalesRatio",
        "priceToFreeCashFlowRatio",
        "priceToOperatingCashFlowRatio",
        "debtToAssetsRatio",
        "debtToEquityRatio",
        "debtToCapitalRatio",
        "longTermDebtToCapitalRatio",
        "financialLeverageRatio",
        "workingCapitalTurnoverRatio",
        "operatingCashFlowRatio",
        "operatingCashFlowSalesRatio",
        "freeCashFlowOperatingCashFlowRatio",
        "debtServiceCoverageRatio",
        "interestCoverageRatio",
        "shortTermOperatingCashFlowCoverageRatio",
        "operatingCashFlowCoverageRatio",
        "capitalExpenditureCoverageRatio",
        "dividendPaidAndCapexCoverageRatio"]

    url = f"https://financialmodelingprep.com/stable/key-metrics?symbol={company_name}&apikey={fmp_api_key}"
    r = requests.get(url)
    ## 22, 23, 24, 25
    annual_reports = list(reversed(r.json()))[-4:]

    for annual_report in annual_reports:
        for (key, value) in annual_report.items():
            if key in key_metrics_to_consider:
                financial_metric_object = db.query(FinancialMetric).filter(
                    and_(
                        FinancialMetric.name == key,
                        FinancialMetric.is_active == True
                    )
                ).first()
                if not financial_metric_object:
                    continue
                financial_metric_map.setdefault(key, []).append(value)


    ratio_url = f"https://financialmodelingprep.com/stable/ratios?symbol={company_name}&apikey={fmp_api_key}"
    ratio_response = requests.get(ratio_url)
    ## 22, 23, 24, 25
    annual_reports_because_of_ratio = list(reversed(ratio_response.json()))[-4:]

    for annual_report in annual_reports_because_of_ratio:
        for (key, value) in annual_report.items():
            if key in ratio_metrics_to_consider:
                financial_metric_object = db.query(FinancialMetric).filter(
                    and_(
                        FinancialMetric.name == key,
                        FinancialMetric.is_active == True
                    )
                ).first()
                if not financial_metric_object:
                    continue
                financial_metric_map.setdefault(key, []).append(value)
    return financial_metric_map

def get_calculated_metrics(db, financial_metric_map, company_name):

    considered_financial_metrics = ["revenue", "total_employee_number"]

    with open("/Users/danielschmidt/Desktop/stock_management_system/Stock_management_fast_api/financial_metric_component/current_financial_metrics_guro_focus.json") as financial_metrics_file:
        financial_metrics = json.load(financial_metrics_file)

    annuals = financial_metrics.get("annual", [])

    revenue_per_employee_map = {}

    for current_year_map in annuals:
        for key, value in current_year_map.items():
            if key not in considered_financial_metrics:
                continue
            financial_metric_object = db.query(FinancialMetric).filter(
            and_(
                FinancialMetric.name == "revenue_per_employee",
                FinancialMetric.is_active == True
            )
            ).first()
            if not financial_metric_object:
                continue
            revenue_per_employee_map.setdefault(key, []).append(value)

    employee_numbers = revenue_per_employee_map.get("total_employee_number", [])
    revenues = revenue_per_employee_map.get("revenue", [])

    if len(employee_numbers) != len(revenues):
        return financial_metric_map

    for idx, employee_number in enumerate(employee_numbers):
        revenue = revenues[idx]
        value = int(revenue / employee_number)
        financial_metric_map.setdefault("total_employee_number", []).append(value)

    return financial_metric_map