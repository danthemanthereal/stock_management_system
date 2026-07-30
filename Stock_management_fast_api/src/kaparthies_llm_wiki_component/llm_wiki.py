from uuid import UUID
from groq import Groq
from sqlalchemy.ext.asyncio import AsyncSession
import os
import json
from dotenv import load_dotenv
from src.bought_stock_component.service import BoughtStockService
from src.kaparthies_llm_wiki_component.prompt import user_prompt_for_ingest, \
    user_prompt_focus_only_strengths, system_prompts_for_focus_only_strengths, system_prompt_for_focus_only_weaknesses, \
    user_prompt_focus_only_weaknesses, get_system_prompt_for_ingest, get_user_prompt_ingest_stock_market_wiki, \
    get_system_prompt_ingest_stock_market_wiki, get_user_prompt_ingest_industry_wiki, \
    get_system_prompt_ingest_industry_wiki, get_system_prompt_bull_factors, get_user_prompt_bull_factors, \
    get_system_prompt_bear_factors, get_user_prompt_bear_factors
from src.watchlist_component.service import WatchlistStockService

load_dotenv()

class LLMWiki:

    def __init__(self, db: AsyncSession, groq_model_name):
        self.db = db
        self.groq_model_name = groq_model_name

    async def ingest(self,
               watch_list_stock_id: int,
               bought_stock_id: int,
               company_name: str,
               ticker: str,
               new_strengths: str,
               new_weaknesses: str,
               new_content: str):

        current_strengths, current_weakness, current_wiki_page = await self.get_strength_weakness_wiki_page(watch_list_stock_id, bought_stock_id)

        new_combined_strengths = self.get_ingest_only_strengths(
            company_name=company_name,
            ticker=ticker,
            current_strengths=current_strengths,
            new_strengths=new_strengths)

        new_combined_weakness = self.get_ingest_only_weakness(
            company_name=company_name,
            ticker=ticker,
            current_weaknesses=current_weakness,
            new_weaknesses=new_weaknesses)

        new_wiki_page = self.ingest_new_wiki_page(
            company_name=company_name,
            ticker=ticker,
            current_wiki_page=current_wiki_page,
            new_content=new_content)

        return new_combined_strengths, new_combined_weakness, new_wiki_page

    async def get_strength_weakness_wiki_page(self, watch_list_stock_id: int, bought_stock_id: int):
        from src.watchlist_component.service import WatchlistStockService
        from src.bought_stock_component.service import BoughtStockService
        watchlist_stock_service = WatchlistStockService(self.db)
        bought_stock_service = BoughtStockService(self.db)

        if watch_list_stock_id:
            return await watchlist_stock_service.get_of_current_watchlist_stock_strengths_weakness_wiki_page_with_id(watch_list_stock_id)
        elif bought_stock_id:
            return await bought_stock_service.get_bought_stock_strengths_weakness_wiki_page_with_id(bought_stock_id)
        return "", "", ""

    def get_ingest_only_strengths(self, company_name, ticker, current_strengths, new_strengths):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        user_prompt = user_prompt_focus_only_strengths(
            company_name=company_name,
            ticker=ticker,
            current_strengths=current_strengths,
            new_strengths=new_strengths
        )

        system_prompt = system_prompts_for_focus_only_strengths()
        response = client.chat.completions.create(
            model=self.groq_model_name,
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
        return content

    def get_ingest_only_weakness(self,company_name, ticker, current_weaknesses, new_weaknesses):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        user_prompt = user_prompt_focus_only_weaknesses(
            company_name=company_name,
            ticker=ticker,
            current_weaknesses=current_weaknesses,
            new_weaknesses=new_weaknesses
        )
        system_prompt = system_prompt_for_focus_only_weaknesses()
        response = client.chat.completions.create(
            model=self.groq_model_name,
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
        return content


    def ingest_new_wiki_page(self, company_name, ticker,current_wiki_page, new_content):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        user_prompt = user_prompt_for_ingest(
            ticker=ticker,
            company_name=company_name,
            existing_body=current_wiki_page,
            source_text=new_content
        )
        system_prompt = get_system_prompt_for_ingest()
        response = client.chat.completions.create(
            model=self.groq_model_name,
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
        return content

    def query_on_wiki_page(self, question: str, current_wiki_page: str):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        system_prompt = self.system_prompt_for_query()

        user_prompt = self.user_prompt_for_query(
            question=question,
            context=current_wiki_page
        )

        response = client.chat.completions.create(
            model=self.groq_model_name,
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
        return content


    def system_prompt_for_query(self):
        return """

        You are a knowledgeable assistant with access to a curated wiki knowledge base.
        Answer the user's question using ONLY the provided wiki pages as your source.
        Cite which wiki pages you drew from using [Page Title] notation.
        If the wiki pages do not contain sufficient information, say so explicitly.
        Be concise but complete.
        """

    def user_prompt_for_query(self, question: str, context):
        return f"""
        ## Question
        {question}

        ## Relevant Wiki Pages
        {context}

        Answer the question based on the wiki content above."""

    async def update_page_strength_weakness_if_company_on_watchlist_or_in_bought(self,
                                                                           company_ticker: str,
                                                                           current_user_id: UUID,
                                                                           new_strengths: str,
                                                                           new_weaknesses: str,
                                                                           new_content: str      ):

        watchlist_stock_service = WatchlistStockService(self.db)

        bought_stock_service = BoughtStockService(self.db)

        if await bought_stock_service.user_already_bought_stock(current_user_id=current_user_id,
                                                                ticker=company_ticker):
            current_bought_stock = await  bought_stock_service.get_of_current_user_stock_by_name(
                current_user_id=current_user_id,
                ticker=company_ticker
            )
            bought_stock_id = current_bought_stock.id
            (
                new_combined_strengths,
                new_combined_weakness,
                new_combined_wiki
            ) = await self.ingest(
                watch_list_stock_id=None,
                bought_stock_id=bought_stock_id,
                company_name="",
                ticker=company_ticker,
                new_strengths=new_strengths,
                new_weaknesses=new_weaknesses,
                new_content=new_content
            )
            await bought_stock_service.update_strength_weakness_wiki_page_of_stock(
                bought_stock_obj=current_bought_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki
            )
        elif await watchlist_stock_service.check_if_user_has_stock_already_in_watchlist(current_user_id=current_user_id,
                                                                                        ticker=company_ticker):
            current_watch_list_stock = await watchlist_stock_service.get_current_stock_of_user(
                current_user_id=current_user_id,
                ticker_of_stock=company_ticker,
            )

            current_watch_list_stock_id = current_watch_list_stock.id

            (
                new_combined_strengths,
                new_combined_weakness,
                new_combined_wiki
            ) = await self.ingest(
                watch_list_stock_id=current_watch_list_stock_id,
                bought_stock_id=None,
                company_name="",
                ticker=company_ticker,
                new_strengths=new_strengths,
                new_weaknesses=new_weaknesses,
                new_content=new_content
            )

            await watchlist_stock_service.update_strength_weakness_wiki_page_of_watchlist_stock(
                watchlist_stock_obj=current_watch_list_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki
            )

    async def ingest_stock_market_wiki_page(self,
                                            new_stock_market_infos,
                                            current_wiki_page):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        user_prompt =  get_user_prompt_ingest_stock_market_wiki(new_stock_market_infos, current_wiki_page)

        system_prompt = get_system_prompt_ingest_stock_market_wiki()
        response = client.chat.completions.create(
            model=self.groq_model_name,
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
        return content

    async def ingest_industry_wiki_page(self,
                                        industry_name: str,
                                        current_wiki_page: str,
                                        new_content: str,
                                        ):

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        user_prompt = get_user_prompt_ingest_industry_wiki(
            current_wiki_page=current_wiki_page,
            industry_name=industry_name,
            new_content=new_content,
        )

        system_prompt = get_system_prompt_ingest_industry_wiki()
        response = client.chat.completions.create(
            model=self.groq_model_name,
            messages=[
                {"role": "system",
                 "content": system_prompt
                 },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ])

        return response.choices[0].message.content

    async def ingest_bear_factors_wiki_page(self,
                                            industry_name: str,
                                            current_bear_factors: str,
                                            new_bear_factors: str,
                                            ):
        client = Groq(api_key=os.getenv("SECOND_GROQ_API_KEY"))
        user_prompt = get_user_prompt_bear_factors(
                industry=industry_name,
            current_bear_factors=current_bear_factors,
            new_content=new_bear_factors,
        )
        system_prompt = get_system_prompt_bear_factors()
        response = client.chat.completions.create(
            model=self.groq_model_name,
            messages=[
                {"role": "system",
                 "content": system_prompt
                 },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ])
        print("response ")
        print(response.choices[0].message.content)
        return json.loads(response.choices[0].message.content).get("bear_factors")

    async def ingest_bull_factors_wiki_page(self,
                                            industry_name: str,
                                            current_bull_factors: str,
                                            new_bull_factors: str,
                                            ):
        client = Groq(api_key=os.getenv("SECOND_GROQ_API_KEY"))
        user_prompt = get_user_prompt_bull_factors(
            industry=industry_name,
            new_content=new_bull_factors,
            current_bull_factors=current_bull_factors,
        )

        system_prompt = get_system_prompt_bull_factors()
        response = client.chat.completions.create(
            model=self.groq_model_name,
            messages=[
                {"role": "system",
                 "content": system_prompt
                 },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ])

        return json.loads(response.choices[0].message.content).get("bull_factors")


