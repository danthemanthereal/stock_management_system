import requests
from src.database.models import FinancialMetric, ProfileMetricConfiguration
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

    selected_profile_id = 1
    annuals = financial_metrics.get("annual", [])
    for current_year_map in annuals:
        for key, value in current_year_map.items():
            if key == "date":
                continue
            financial_metric_object = (
                db.query(FinancialMetric)
                .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
                .filter(
                    and_(
                        FinancialMetric.name == key,
                        ProfileMetricConfiguration.profile_id == selected_profile_id,
                        ProfileMetricConfiguration.is_active == True
                    )
                )
                .first()
            )
            if not financial_metric_object:
                continue
            financial_metric_map.setdefault(key, []).append(value)

    return financial_metric_map


def get_financial_metrics_with_alpha_ventage_api(db, financial_metric_map, company_name):
    alpha_vantage_api_key = "QZX1ZGLLW5C7LMB0"
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={company_name}&apikey={alpha_vantage_api_key}'
    r = requests.get(url)
    financial_metric_to_get = ["costOfRevenue"]
    selected_profile_id = 1


    ## 22, 23, 24, 25

    data = r.json()
    annual_reports = list(reversed(data.get('annualReports', [])))[-4:]
    for annual_report in annual_reports:
        for (key, value) in annual_report.items():
            if key in financial_metric_to_get:
                financial_metric_object = (
                db.query(FinancialMetric)
                .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
                .filter(
                    and_(
                        FinancialMetric.name == key,
                        ProfileMetricConfiguration.profile_id == selected_profile_id,
                        ProfileMetricConfiguration.is_active == True
                    )
                )
                .first()
            )
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
    "freeCashFlowToFirm",
    "netDebtToEBITDA"
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
    data = r.json()
    annual_reports = list(reversed(data.get('annualReports', [])))[-4:]
    selected_profile_id = 1
    for annual_report in annual_reports:
        for (key, value) in annual_report.items():
            if key in key_metrics_to_consider:
                financial_metric_object = (
                db.query(FinancialMetric)
                .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
                .filter(
                    and_(
                        FinancialMetric.name == key,
                        ProfileMetricConfiguration.profile_id == selected_profile_id,
                        ProfileMetricConfiguration.is_active == True
                    )
                )
                .first()
            )
                if not financial_metric_object:
                    continue
                financial_metric_map.setdefault(key, []).append(value)


    ratio_url = f"https://financialmodelingprep.com/stable/ratios?symbol={company_name}&apikey={fmp_api_key}"
    ratio_response = requests.get(ratio_url)
    ## 22, 23, 24, 25
    annual_reports_because_of_ratio = list(reversed(ratio_response.get('annualReports', [])))[-4:]

    for annual_report in annual_reports_because_of_ratio:
        for (key, value) in annual_report.items():
            if key in ratio_metrics_to_consider:
                financial_metric_object = (
                db.query(FinancialMetric)
                .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
                .filter(
                    and_(
                        FinancialMetric.name == key,
                        ProfileMetricConfiguration.profile_id == selected_profile_id,
                        ProfileMetricConfiguration.is_active == True
                    )
                )
                .first()
            )
                if not financial_metric_object:
                    continue
                financial_metric_map.setdefault(key, []).append(value)
    return financial_metric_map

def get_calculated_metrics(db, financial_metric_map, company_name):

    considered_financial_metrics = ["revenue",
                                    "total_employee_number",
                                    "total_equity",
                                    "total_liabilities",
                                    "total_current_liabilities",
                                    "cash_and_cash_equivalents",
                                    "total_free_cash_flow",
                                    "total_current_assets",
                                    "total_non_current_assets",
                                    "total_assets",
                                    "good_will"]

    with open("/Users/danielschmidt/Desktop/stock_management_system/Stock_management_fast_api/financial_metric_component/current_financial_metrics_guro_focus.json") as financial_metrics_file:
        financial_metrics = json.load(financial_metrics_file)

    annuals = financial_metrics.get("annual", [])

    needed_financial_metrics_map = {}

    for current_year_map in annuals:
        for key, value in current_year_map.items():
            if key not in considered_financial_metrics:
                continue

            needed_financial_metrics_map.setdefault(key, []).append(value)

    employee_numbers = needed_financial_metrics_map.get("total_employee_number", [])
    revenues = needed_financial_metrics_map.get("revenue", [])
    total_equity = needed_financial_metrics_map.get("total_equity", [])
    total_liabilities = needed_financial_metrics_map.get("total_liabilities", [])
    total_current_liabilities = needed_financial_metrics_map.get("total_current_liabilities", [])
    cash_and_cash_equivalents = needed_financial_metrics_map.get("cash_and_cash_equivalents", [])
    total_current_assets = needed_financial_metrics_map.get("total_current_assets", [])
    total_non_current_assets = needed_financial_metrics_map.get("total_non_current_assets", [])
    total_assets = needed_financial_metrics_map.get("total_assets", [])
    total_good_will = needed_financial_metrics_map.get("good_will", [])

    selected_profile_id = 1
    revenue_per_employee_object = (
                db.query(FinancialMetric)
                .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
                .filter(
                    and_(
                        FinancialMetric.name == "revenue_per_employee",
                        ProfileMetricConfiguration.profile_id == selected_profile_id,
                        ProfileMetricConfiguration.is_active == True
                    )
                )
                .first()
            )
    if len(employee_numbers) == len(revenues) and revenue_per_employee_object:
        for idx, employee_number in enumerate(employee_numbers):
            revenue = revenues[idx]
            value = revenue / employee_number
            financial_metric_map.setdefault("revenue_per_employee", []).append(value)

    gearing_object = (
        db.query(FinancialMetric)
        .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
        .filter(
            and_(
                FinancialMetric.name == "gearing",
                ProfileMetricConfiguration.profile_id == selected_profile_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        .first()
    )

    if len(total_equity) == len(total_liabilities) and len(total_liabilities) == len(cash_and_cash_equivalents) and gearing_object:
        for idx, current_equity_in_year in enumerate(total_equity):
            current_total_liability = total_liabilities[idx]
            current_cash_and_cash_equivalent = cash_and_cash_equivalents[idx]
            net_debt = current_total_liability - current_cash_and_cash_equivalent
            value = net_debt / current_equity_in_year
            financial_metric_map.setdefault("gearing", []).append(value)


    dynamic_debt_degree_object = (
        db.query(FinancialMetric)
        .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
        .filter(
            and_(
                FinancialMetric.name == "dynamic debt degree",
                ProfileMetricConfiguration.profile_id == selected_profile_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        .first()
    )
    if len(total_equity) == len(total_liabilities) and len(total_liabilities) == len(cash_and_cash_equivalents) and dynamic_debt_degree_object:
        for idx, current_equity_in_year in enumerate(total_equity):
            current_total_liability = total_liabilities[idx]
            current_cash_and_cash_equivalent = cash_and_cash_equivalents[idx]
            net_debt = current_total_liability - current_cash_and_cash_equivalent
            value = net_debt / current_equity_in_year
            financial_metric_map.setdefault("dynamic debt degree", []).append(value)


    current_asset_intensity_object = (
        db.query(FinancialMetric)
        .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
        .filter(
            and_(
                FinancialMetric.name == "current_asset_intensity",
                ProfileMetricConfiguration.profile_id == selected_profile_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        .first()
    )

    if len(total_current_assets) == len(total_assets) and current_asset_intensity_object:
        for idx, current_total_asset in enumerate(total_assets):
            current_current_asset = total_current_assets[idx]
            value = current_current_asset / current_total_asset
            financial_metric_map.setdefault("current_asset_intensity", []).append(value)



    non_current_asset_intensity_object =  (
        db.query(FinancialMetric)
        .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
        .filter(
            and_(
                FinancialMetric.name == "non_current_asset_intensity",
                ProfileMetricConfiguration.profile_id == selected_profile_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        .first()
    )
    if len(total_non_current_assets) == len(total_assets) and non_current_asset_intensity_object:
        for idx, current_total_asset in enumerate(total_assets):
            current_non_current_asset = total_non_current_assets[idx]
            value = current_non_current_asset / current_total_asset
            financial_metric_map.setdefault("non_current_asset_intensity", []).append(value)


    asset_cover_degree_one_object =    (
        db.query(FinancialMetric)
        .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
        .filter(
            and_(
                FinancialMetric.name == "asset_cover_ratio_one",
                ProfileMetricConfiguration.profile_id == selected_profile_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        .first()
    )

    if len(total_equity) == len(total_assets) and asset_cover_degree_one_object:
        for idx, current_equity_in_year in enumerate(total_equity):
            current_total_asset = total_assets[idx]
            value = current_equity_in_year / current_total_asset
            financial_metric_map.setdefault("asset_cover_ratio_one", []).append(value)

    asset_cover_degree_two_object =  (
        db.query(FinancialMetric)
        .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
        .filter(
            and_(
                FinancialMetric.name == "asset_cover_ratio_two",
                ProfileMetricConfiguration.profile_id == selected_profile_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        .first()
    )

    if len(total_equity) == len(total_assets) and len(total_assets) == len(total_liabilities) and asset_cover_degree_two_object:
        for idx, current_equity_in_year in enumerate(total_equity):
            current_total_asset = total_assets[idx]
            current_long_term_liabilities = total_liabilities[idx] - total_current_liabilities[idx]
            value = (current_equity_in_year + current_long_term_liabilities ) / current_total_asset
            financial_metric_map.setdefault("asset_cover_ratio_two", []).append(value)


    good_will_object =   (
        db.query(FinancialMetric)
        .join(ProfileMetricConfiguration, ProfileMetricConfiguration.metric_id == FinancialMetric.id)
        .filter(
            and_(
                FinancialMetric.name == "good_will_ratio",
                ProfileMetricConfiguration.profile_id == selected_profile_id,
                ProfileMetricConfiguration.is_active == True
            )
        )
        .first()
    )


    if len(total_good_will) == len(total_equity) and good_will_object:
        for idx, current_equity_in_year in enumerate(total_equity):
            current_good_will = total_good_will[idx]
            value = current_good_will / current_equity_in_year
            financial_metric_map.setdefault("good_will_ratio", []).append(value)


    return financial_metric_map