import requests

def get_financial_metrics_by_guro_focus(company: str):
    url = f"https://www.gurufocus.com/reader/_api/stocks/US04EJ/financial?v={company}" # irgend so eine id ?

    payload = {
        "start_date": "2022-01-01",
        "end_date": "2025-12-31",
        "target_currency": "USD",
        "fields": []
    }

    response = requests.post(url, json=payload)
    data = response.json()

    print(data["annual"][0])