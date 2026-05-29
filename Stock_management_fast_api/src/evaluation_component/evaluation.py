from uuid import UUID

from groq import Groq
import re
import json
from src.watchlist_component.service import WatchlistStockService
import os
from dotenv import load_dotenv
from src.combining_stock_infos_llm.combine_stock import CombineComponent
from src.ticker_stock_component.ticker_stock import TickerStock

load_dotenv()

class Evaluator:

    def __init__(self, db, model_name):
        self.db = db
        self.model_name = model_name

    def safe_parse(self,content):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"strengths": [], "weaknesses": []}

    def evaluate_new_information(self, current_user_id: UUID,
                                 company_name: str,
                                 new_strength: str,
                                 new_weakness: str):
        current_strengths, current_weaknesses= self.get_strength_weakness_of_stock(current_user_id, company_name, new_strength, new_weakness)
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_user_prompt(current_strengths, new_strength, current_weaknesses,new_weakness)
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

    def get_strength_weakness_of_stock(self, current_user_id: UUID, company_name: str, new_strength: str, new_weakness: str):
        watch_list_service = WatchlistStockService(self.db)

        get_ticker_component = TickerStock()
        ticker = get_ticker_component.get_ticker_of_a_stock(company_name)

        if watch_list_service.check_if_user_has_stock_already_in_watchlist(current_user_id, ticker):
            current_watchlist_stock = watch_list_service.get_current_stock_of_user(current_user_id, ticker)
            current_strengths = current_watchlist_stock.strength
            current_weakness = current_watchlist_stock.weakness

            combiner = CombineComponent(os.getenv("GROQ_API_KEY"))
            strengths, weaknesses = combiner.get_combination(current_strengths, current_weakness, new_strength, new_weakness)

            current_watchlist_stock.strength = "\n".join(f"• {s}" for s in strengths)
            current_watchlist_stock.weakness = "\n".join(f"• {w}" for w in weaknesses)
            self.db.commit()
            self.db.refresh(current_watchlist_stock)
            return current_strengths, current_weakness
        watch_list_service.add_to_current_user_to__watchlist(company_name,
                                                             ticker,
                                                             new_strength,
                                                             new_weakness,
                                                             current_user_id)
        return "", ""

    def get_system_prompt(self) -> str:
        return """
        <role>
        You are an expert corporate strategist and financial analyst specializing in risk assessment and company evaluations.
        </role>
    
        <context>
        You will be provided with:
        1. The Current Strengths and Current Weaknesses of a specific company.
        2. The New Strengths and New Weaknesses that have recently emerged.
        </context>
    
        <instructions>
        Your task is to analyze how the newly emerged information impacts the company's overall situation. 
    
        Follow these analytical steps:
        1. Assess the New Strengths: Do they successfully mitigate or neutralize the current weaknesses?
        2. Assess the New Weaknesses: How severely do they damage the company or undermine its existing strengths?
        3. Determine the Trajectory: Based on the shift from current to new, has the overall situation Improved, Worsened, or remained Unchanged?
        4. Answer only in German. 
    
        CRITICAL CONSTRAINTS:
        - You MUST base your entire analysis, reasoning, and recommendation STRICTLY on the provided context. 
        - DO NOT hallucinate, assume facts, or use outside knowledge about the company.
        - Your output MUST be ONLY a valid, parseable JSON object. Do not include any markdown formatting (like ```json), preambles, or concluding remarks.
        </instructions>
    
        <output_format>
        {
          "trajectory": "State exactly one of: 'Improved', 'Worsened', 'Unchanged'",
          "reasoning": "Explain clearly why the situation changed, referencing the provided strengths and weaknesses.",
          "recommendation": "Provide a brief recommendation based solely on the provided data."
        }
        </output_format>
        """


    def get_user_prompt(self,current_strengths: str,
                        new_strengths: str,
                        current_weaknesses: str,
                        new_weaknesses: str) -> str:
        return f"""
        Please analyze the following company data and provide the evaluation in the requested JSON format.
    
        <current_strengths>
        {current_strengths}
        </current_strengths>
    
        <current_weaknesses>
        {current_weaknesses}
        </current_weaknesses>
    
        <new_strengths>
        {new_strengths}
        </new_strengths>
    
        <new_weaknesses>
        {new_weaknesses}
        </new_weaknesses>
        """
