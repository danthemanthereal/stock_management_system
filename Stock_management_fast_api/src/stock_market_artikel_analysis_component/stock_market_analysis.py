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


            return response.choices[0].message.content
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
    """