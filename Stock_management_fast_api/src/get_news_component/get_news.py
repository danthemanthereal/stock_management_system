from datetime import datetime, timedelta
from gnews import GNews
import requests

from src.configs.used_model import STOCK_MARKET_ANALYSIS_MODEL
from src.stock_market_artikel_analysis_component.stock_market_analysis import StockMarketAnalysis


class NewsFinderComponent:

    def __init__(self, finhub_api_key):
        self.finhub_api_key = finhub_api_key


    def get_all_news_of_stock(self, ticker: str):
        head_line_url_news = []
       # head_line_url_news = self.get_news_of_finhub_api(ticker, head_line_url_news)
        head_line_url_news = self.get_news_with_G_news(ticker, head_line_url_news)
        return head_line_url_news


    def get_news_of_finhub_api(self, ticker: str, headline_url_news):
        today = datetime.utcnow().date()
        two_days_ago = today - timedelta(days=2)

        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={two_days_ago}&to={today}&token={self.finhub_api_key}"
        response = requests.get(url)
        data = response.json()



        for news in data:
            headline_url_news.append({
            "headline": news["headline"],
            "url": news["url"],
            })


        return headline_url_news

    def get_news_with_G_news(self, ticker: str, headline_url_news):
        google_news = GNews(language='de', country='DE', period='1d')

        stock_news = google_news.get_news(f'{ticker}  Aktie news')

        for artikel in stock_news:
                headline_url_news.append({
            "headline": artikel['title'],
            "url": artikel['url']
        })

        return headline_url_news

    def get_stock_market_news_with_G_news(self,):

        headline_url_news = []
        google_news = GNews(language='de', country='DE', period='1d')

        stock_news = google_news.get_news(f'Aktienmarkt news')

        stock_market_analysis = StockMarketAnalysis(
            model_name=STOCK_MARKET_ANALYSIS_MODEL,
        )

        for artikel in stock_news:
                summary = stock_market_analysis.get_stock_market_analysis_of_url(artikel['url'])
                headline_url_news.append({
            "headline": artikel['title'],
            "ai_summary": summary,
        })

        return headline_url_news