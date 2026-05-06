import requests
from database.models import FinancialMetric
from playwright.async_api import async_playwright
import json
from sqlalchemy import and_


def get_financial_metrics_by_guro_focus(json_copied: str,db):
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
    data = f'''
            {json_copied}  
    '''
    

    parsed = json.loads(data)
    annuals = parsed["annual"]
    financial_metric_map = {}
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
