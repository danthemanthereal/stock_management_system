from uuid import UUID

from groq import Groq
import re
import json
from src.watchlist_component.service import WatchlistStockService
import os
from dotenv import load_dotenv
from src.ticker_stock_component.ticker_stock import TickerStock
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki
from src.bought_stock_component.service import BoughtStockService
from src.html__text_parser_component.bs4_text_parser import BS4TextParser
from src.youtube_transcript_component.yt_transcript_component import \
    YoutubeTranscriptComponent

load_dotenv()


class Evaluator:

    def __init__(self, db, model_name):
        self.db = db
        self.model_name = model_name

    def safe_parse(self, content):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"strengths": [], "weaknesses": []}

    async def evaluate_new_information(self, current_user_id: UUID,
                                 company_name: str,
                                 new_strength: str,
                                 new_weakness: str,
                                 used_url: str,
                                 used_yt_url: str ):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        watchlist_service = WatchlistStockService(self.db)
        ticker_component = TickerStock()
        ticker = ticker_component.get_ticker_of_a_stock(company_name)
        (current_strengths,
         current_weaknesses,
         current_wiki_page) = watchlist_service.get_of_current_watchlist_stock_strengths_weakness_wiki_page(
            current_user_id, ticker
        )

        current_watchlist_id = watchlist_service.get_watchlist_stock_id_by_ticker(ticker)

        await self.update_strength_weakness_wiki_page(
            watchlist_stock_id=current_watchlist_id,
            bought_stock_id=None,
            company_name=company_name,
            ticker=ticker,
            new_strengths=new_strength,
            new_weaknesses=new_weakness,
            url=used_url,
            yt_url=used_yt_url
        )


        system_prompt = self.get_system_prompt()
        user_prompt = self.get_user_prompt(company_name,
                                           ticker,
                                           current_strengths,
                                           new_strength,
                                           current_weaknesses,
                                           new_weakness,
                                           current_wiki_page)
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system",
                 "content": system_prompt
                 },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ])

        content = response.choices[0].message.content
        data = self.safe_parse(content)
        trajectory = data.get("trajectory", "")
        reasoning = data.get("reasoning", "")
        recommendation = data.get("recommendation", "")

        return trajectory, reasoning, recommendation

    def get_system_prompt(self) -> str:
        return """
You are a professional equity research analyst.

Your task is to compare:
- Existing strengths
- Existing weaknesses
- Existing company wiki / analysis
WITH
- New strengths
- New weaknesses

You must evaluate whether the NEW information improves, worsens, or does not materially change the overall company trajectory and investment thesis.

IMPORTANT:
- Focus on long-term business fundamentals
- Do NOT focus on short-term stock price movement
- Weigh strengths against weaknesses carefully
- Strong new risks may outweigh multiple small strengths
- Strong strategic improvements may outweigh existing weaknesses
- Be analytical and evidence-based
- Never hallucinate information

---

You MUST return ONLY valid JSON.

REQUIRED JSON FORMAT:

{
  "trajectory": "IMPROVED | WORSENED | UNCHANGED",
  "reasoning": "Short analytical explanation",
  "recommendation": "BUY | SELL | HOLD"
}

---

FIELD DEFINITIONS:

trajectory:
- Verbessert → company outlook improved
- Verschlechtert → company outlook worsened
- Gleich → no major fundamental change

recommendation:
- Nach kaufen → positive long-term thesis strengthened
- Verkaufen möglicherweise → negative developments materially weaken thesis
- Halten → mixed or unchanged outlook

reasoning:
- 5-10 concise analytical sentences
- Explain WHY the trajectory changed or stayed unchanged
- Answer only in german.
"""

    def get_user_prompt(self,
                        company_name: str,
                        ticker: str,
                        current_strengths: str,
                        new_strengths: str,
                        current_weaknesses: str,
                        new_weaknesses: str,
                        current_wiki_page: str) -> str:
        return f"""
        # Company
        {company_name} ({ticker})
        
        ---
        
        # Current Strengths
        {current_strengths or "None"}
        
        ---
        
        # Current Weaknesses
        {current_weaknesses or "None"}
        
        ---
        
        # Current Wiki / Company Analysis
        {current_wiki_page or "None"}
        
        ---
        
        # New Strengths / Positive Developments
        {new_strengths or "None"}
        
        ---
        
        # New Weaknesses / Negative Developments
        {new_weaknesses or "None"}
        
        ---
        
        # Task
        
        Evaluate whether the NEW information materially improves, worsens, or does not significantly change the overall investment thesis and company outlook.
        
        You must:
        - Compare NEW information against EXISTING company knowledge
        - Determine whether the overall situation improved, worsened, or stayed mostly unchanged
        - Consider both positive and negative developments together
        - Focus on long-term business impact, not short-term market reactions
        - Answer only in german.
        
        Return the result in the required format.
"""
    async def update_strength_weakness_wiki_page(self,
                                                 watchlist_stock_id: int,
                                                 bought_stock_id: int,
                                                 company_name: str,
                                                 ticker: str,
                                                 new_strengths,
                                                 new_weaknesses,
                                                 url: str,
                                                 yt_url: str):
        llm_wiki_component = LLMWiki(db=self.db,
                                     groq_model_name=self.model_name)

        new_content =""
        if url:
            html_parser = BS4TextParser()
            new_content = await html_parser.get_website_text(url)

        if yt_url:
            yt_transcript_component = YoutubeTranscriptComponent()
            new_content = yt_transcript_component.get_summary_of_yt_video(yt_url)

        (new_combined_strengths, new_combined_weakness, new_combined_wiki_page) = llm_wiki_component.ingest(
            watch_list_stock_id=watchlist_stock_id,
            bought_stock_id=bought_stock_id,
            company_name=company_name,
            ticker=ticker,
            new_strengths=new_strengths,
            new_weaknesses=new_weaknesses,
            new_content=new_content
        )

        if watchlist_stock_id:
            watchlist_stock_service = WatchlistStockService(db=self.db)
            watchlist_stock = watchlist_stock_service.get_watch_list_stock_with_id(watchlist_stock_id)
            watchlist_stock_service.update_strength_weakness_wiki_page_of_watchlist_stock(
                watchlist_stock_obj=watchlist_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki_page
            )

        elif bought_stock_id:
            bought_stock_service = BoughtStockService(db=self.db)
            bought_stock = bought_stock_service.get_bought_stock_by_id(bought_stock_id)
            bought_stock.update_strength_weakness_wiki_page_of_bought_stock(
                bought_stock_obj=bought_stock,
                new_combined_strengths=new_combined_strengths,
                new_combined_weakness=new_combined_weakness,
                new_combined_wiki_page=new_combined_wiki_page
            )
