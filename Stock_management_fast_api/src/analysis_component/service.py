import json

from src.configs.used_model import STRENGTH_WEAKNESS_MODEL
from src.strength_weakness_company_component.strenth_weakness_comapany import StrengthWeaknessOfCompanyComponent


class AnalysisService:

    def __init__(self,):
        pass

    async def analyse_url(self, url: str):
        strength_weakness_company_component = StrengthWeaknessOfCompanyComponent(
            groq_model_name=STRENGTH_WEAKNESS_MODEL
        )
        companies_array = await strength_weakness_company_component.get_strength_weakness_of_company(url)

        if isinstance(companies_array, str):
            try:
                return json.loads(companies_array)
            except json.JSONDecodeError:
                return []

        return companies_array

    async def analyse_yt_video(self, yt_url: str):
        strength_weakness_company_component = StrengthWeaknessOfCompanyComponent(
            groq_model_name=STRENGTH_WEAKNESS_MODEL
        )
        companies_array = strength_weakness_company_component.get_strength_weakness_of_youtube(yt_url)

        if isinstance(companies_array, str):
            try:
                return json.loads(companies_array)
            except json.JSONDecodeError:
                return []
        return companies_array