from typing import Dict
import re
import json
from groq import Groq
from src.html__text_parser_component.bs4_text_parser import BS4TextParser
from src.industry_ai_evaluation_compoment.prompts import get_system_prompt_bear_and_bull_factor, \
    get_user_prompt_bear_and_bull_factors


class IndustryAIEvaluation:

    def __init__(self, groq_model_name: str,
                 api_key: str,
                 ):
        self.groq_model_name = groq_model_name
        self.api_key = api_key



    async def get_bear_and_bull_factors_by_url(self,
                                               industry: str,
                                               url: str):
        client = Groq(api_key=self.api_key)
        website_parser = BS4TextParser()

        text = await website_parser.get_website_text(url)

        system_prompt = get_system_prompt_bear_and_bull_factor()

        user_prompt = get_user_prompt_bear_and_bull_factors(
            industry=industry,
            content=text
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
        data = self.parse_bear_bull_factors(content)
        bear_factors = data.get("bear_factors", "")
        bull_factors = data.get("bull_factors", "")

        return bear_factors, bull_factors

    def parse_bear_bull_factors(self, llm_output: str) -> Dict[str, str]:


        if not llm_output:
            return {"bear_factors": "", "bull_factors": ""}

        text = llm_output.strip()


        text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()


        try:
            data = json.loads(text)
            return {
                "bear_factors": str(data.get("bear_factors", "") or ""),
                "bull_factors": str(data.get("bull_factors", "") or "")
            }
        except json.JSONDecodeError:
            pass


        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return {
                    "bear_factors": str(data.get("bear_factors", "") or ""),
                    "bull_factors": str(data.get("bull_factors", "") or "")
                }
            except json.JSONDecodeError:
                pass


        bear_match = re.search(r'"bear_factors"\s*:\s*"([^"]*)"', text)
        bull_match = re.search(r'"bull_factors"\s*:\s*"([^"]*)"', text)

        return {
            "bear_factors": bear_match.group(1) if bear_match else "",
            "bull_factors": bull_match.group(1) if bull_match else ""
        }


