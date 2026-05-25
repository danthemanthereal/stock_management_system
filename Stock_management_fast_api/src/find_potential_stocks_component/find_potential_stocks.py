import numpy as np
import pandas as pd
import requests
from finvizfinance.screener.overview import Overview

class FindPotentialStocks:
    def find_potential_stocks_for_current_user(self,filters: dict):
        f = Overview()
        f.set_filter(filters_dict=filters)

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        import finvizfinance.util as util
        original_web_scrap = util.web_scrap

        def patched_web_scrap(url, params, timeout=30):  # Timeout erhöhen
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=timeout)
                resp.raise_for_status()
                return resp.text
            except requests.exceptions.Timeout as e:
                raise requests.exceptions.Timeout(f"Timeout für {url}: {e}")

        util.web_scrap = patched_web_scrap

        try:
            df = f.screener_view()
        finally:
            util.web_scrap = original_web_scrap

        df = df.astype(object)

        df = df.where(pd.notnull(df) & ~df.isin([np.inf, -np.inf]), None)

        return {
            "count": len(df),
            "data": df.to_dict(orient="records")
        }