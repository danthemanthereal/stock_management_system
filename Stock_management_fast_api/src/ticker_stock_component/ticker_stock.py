import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TickerStock:

    def __init__(self):
        pass


    def get_ticker_of_a_stock(self, company_name):

        url = "https://financialmodelingprep.com/stable/search-name"

        params = {
            "query": company_name,
            "apikey": os.getenv("FMP_API_KEY")
        }

        response = requests.get(url, params=params)
        print("response in method ", response)
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}")
        print("json response", response.json())
        return response.json().get("symbol", "")