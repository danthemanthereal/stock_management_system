from groq import Groq
from sqlalchemy.ext.asyncio import AsyncSession
import os
from dotenv import load_dotenv
from src.kaparthies_llm_wiki_component.prompt import user_prompt_for_ingest, \
    user_prompt_focus_only_strengths, system_prompts_for_focus_only_strengths, system_prompt_for_focus_only_weaknesses, \
    user_prompt_focus_only_weaknesses, get_system_prompt_for_ingest

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
