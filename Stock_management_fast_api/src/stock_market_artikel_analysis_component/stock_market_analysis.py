import json
import re

from dotenv import load_dotenv
import os

from groq import Groq

from src.configs.used_model import STOCK_MARKET_ANALYSIS_MODEL
from src.html__text_parser_component.bs4_text_parser import BS4TextParser

load_dotenv()

class StockMarketAnalysis:

    def __init__(self,
                 model_name:str):
        self.model_name = model_name

    async def get_stock_market_analysis_of_url(self, url:str)->str:

        try:
            website_parser = BS4TextParser()

            text = await website_parser.get_website_text(url)

            system_prompt = self.get_system_prompt()

            user_prompt = self.get_user_prompt(text)

            client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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


            return self.safe_parse_llm_json(response.choices[0].message.content).get('answer', "")
        except Exception as e:
            print(e)
            return ""




    def get_system_prompt(self):
        return """
        You are a financial text analyst. Your task is to analyze a given text about the stock market situation.

Follow these steps:
1. Summarize the text briefly and objectively (max. 5–10 sentences).
2. Explain the key events or relationships mentioned (e.g., interest rate decisions, corporate earnings, geopolitical risks).
3. Finally, assess the **sentiment of the text** – not your own opinion, but the implicit or explicit tendency of the author.
   - Possible ratings: "positive", "negative", or "neutral".
   - Justify the rating with specific words or phrases from the text.
4. Answer only in german.    

Important: Do not use any external knowledge or current data outside the text. Only what is stated in the text counts.
        """

    def get_user_prompt(self,  text:str):
        return f"""
    The following text describes the current situation in the stock markets:

    {text}
    
    Please perform the analysis – summary, explanation of key points, and sentiment assessment (positive / negative / neutral) based solely on the text above.
    
    Output only a valid json object in this format: 
    
    {{"answer": "[Your answer of the analysis]"  }}
    
    Also in your analysis answer, make no extra comments or reasoning steps, do direct your analysis. 
    Also the answer of the analysis should contain only a written text. If necessary, do paragraphs with headlines
    but not in a json style. 
    """

    import json
    import re
    from typing import Dict, Any

    def safe_parse_llm_json(self, content: str) -> Dict[str, Any]:

        if not content:
            return {"answer": ""}

        cleaned = content.strip()


        code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        match = re.search(code_block_pattern, cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()

        first_brace = cleaned.find('{')
        if first_brace != -1:
            cleaned = cleaned[first_brace:]
            last_brace = cleaned.rfind('}')
            if last_brace != -1:
                cleaned = cleaned[:last_brace + 1]

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and "answer" in parsed:
                return parsed
            elif isinstance(parsed, dict):

                return {"answer": json.dumps(parsed)}
            elif isinstance(parsed, str):
                return {"answer": parsed}
            else:
                return {"answer": str(parsed)}
        except json.JSONDecodeError:
            pass


        fallback_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if fallback_match:
            try:
                parsed = json.loads(fallback_match.group())
                if isinstance(parsed, dict):
                    return parsed
                else:
                    return {"answer": str(parsed)}
            except json.JSONDecodeError:
                pass

        return {"answer": content if content else ""}