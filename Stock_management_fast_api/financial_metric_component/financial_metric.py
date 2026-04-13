import requests
from database.models import FinancialMetric


def get_financial_metrics_by_guro_focus(company: str, db):
    url = f"https://www.gurufocus.com/reader/_api/stocks/US04EJ/financial?v={company}"

    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjhjNzQzZTA4ZjdlYzE3OTNkZjE1YmJiNzA3ZWQyOTEwZDM2OTg2NjBmMzEwZDdhOWI1ZGM4NTA4MmZjMzc5YTYyYWJlODZjNjVlN2M2YmY2In0.eyJhdWQiOiIyIiwianRpIjoiOGM3NDNlMDhmN2VjMTc5M2RmMTViYmI3MDdlZDI5MTBkMzY5ODY2MGYzMTBkN2E5YjVkYzg1MDgyZmMzNzlhNjJhYmU4NmM2NWU3YzZiZjYiLCJpYXQiOjE3NzYwMTk2NDMsIm5iZiI6MTc3NjAxOTY0MywiZXhwIjoxNzgxMjAzNjQzLCJzdWIiOiIxMzEyNDUwIiwic2NvcGVzIjpbXX0.l-z2TfYtGgspNB75Qv-yg3gzPyjXxG7Rr7FK2gFLwUDFu-V9Eeurz3Ug5OJ51TrmZn5YwtpSV3Ol7tCvEU1MJ8jKL1_LToMmSfNiH3PxYXZQY4RaaODZBnnQLRfOkhqFfiMCffCfqNy4UxzAGKn9yDIDWobt9lyz1QCd0jIXPQGRXvGPxKF02DKYsB9b-maQbE13_HH64jYV-A_sGldXiDIUcKcXYb_LeypX6wu20Dr9r_DbagRkS7_iZWYF-Syj6pYZXaD1PY0wPJmwCsvok8e-BMX3CjFESCtJisEQDq6UdD9ruS6T_R03CtwQl2o_nTtOUp4Z0Ku0M7tYcjUY1PMaw5kiLj2dtsx3Ad3szIYRIZyQ9ddTyQkY8HD8pTUKOXnuHr-0eTaCs43itik3JBQCkEsJHsYtuBe0lyRdhYLwlLj5_Z14RlEp-UUpYLGVYjJ-QzE764D8bfp7VqlitD1ZOBs1REMO47lZd9_Ipgh8VyWtufaZFbww0jPd3QkVSYA9SUecfaGXXyajvRfuBVLUA3IAkLGsw8SybLRE-6ZPdLvIqn5jHSv8v4AxYKKbPwcmhEhiijiFtvXyxLL3Qg3elTAcqPNdvz9bNxG8Te75c0kApV6OSu1DYdWVS1u5erOC15r1BVo-7gFQyqdT8DXRn_yEL7_ZKpfR-9Qseh0",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "start_date": "2022-01-01",
        "end_date": "2025-12-31",
        "target_currency": "USD",
        "fields": []
    }

    response = requests.post(url, json=payload, headers=headers)
    yearly_data = response.json()["annual"]
    for key in yearly_data[0].keys():
        metric = FinancialMetric(
            name=key,
            should_rise=True,
            reference_value=10,
            unit="%"
        )
        db.add(metric)

    db.commit()
    ttm_data =  response.json()["ttm"]
    result = {}
    # last years
    for entry in yearly_data:
        for key, value in entry.items():
            financial_metric = db.query(FinancialMetric).filter(FinancialMetric.name == key).first()
            if not financial_metric:
                continue

            if key not in result:
                result[key] = []
            result[key].append(value)

    # TODO : check yearly ttm always last ?
    """for entry in ttm_data:
        for key, value in entry.items():
            if key not in result:
                result[key] = []
            result[key].append(value)"""

    return result