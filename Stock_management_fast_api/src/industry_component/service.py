from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.used_model import LLM_WIKI_MODEL
from src.database.models import Industry
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki


class IndustryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_industry_wiki_page_of_current_user(self,
                                               current_user_id: UUID
                                               ):
        result = await self.db.execute(
            select(Industry)
            .where(Industry.user_id == current_user_id)
        )

        rows = result.scalars().all()
        return list(rows)

    async def add_to_current_user_new_industry(self, industry_name: str,
                                               current_user_id: UUID):
        try:
            new_industry = Industry(
                industry_name=industry_name,
                user_id=current_user_id,
                wiki_page="",
                bear_factors="",
                bull_factors=""
            )

            self.db.add(new_industry)
            await self.db.commit()
            await self.db.refresh(new_industry)
        except Exception as e:
            print(e)

    async def get_industries_of_current_user(self, current_user_id: UUID):
        result = await self.db.execute(
            select(Industry.industry_name)
            .where(Industry.user_id == current_user_id)
        )

        rows = result.scalars().all()
        return list(rows)

    async def get_current_wiki_page_of_industry_of_current_user(self,
                                                                industry_name: str,
                                                                current_user_id: UUID) ->str:
        try:
            result = await self.db.execute(
                select(Industry.wiki_page)
                .where(Industry.user_id == current_user_id,
                       Industry.industry_name == industry_name
                       )
            )

            return result.scalars().first()
        except Exception as e:
            print(e)
            return ""

    async def update_wiki_page_of_selected_industry_of_current_user(
            self,
            industry_name: str,
            current_user_id: UUID,
            new_wiki_page: str
    ):

        result = await self.db.execute(
            select(Industry)
            .where(Industry.user_id == current_user_id,
                   Industry.industry_name == industry_name
                   )
        )

        industry = result.scalars().first()
        if not industry:
            return False

        industry.wiki_page = new_wiki_page

        await self.db.commit()

        await self.db.refresh(industry)
        return True

    async def get_bear_and_bull_factors_of_current_industry_of_current_user(self,
                                                                            industry_name: str,
                                                                            current_user_id: UUID
                                                                            ):
        result = await self.db.execute(
            select(Industry.bull_factors, Industry.bear_factors)
            .where(Industry.user_id == current_user_id,
                   Industry.industry_name == industry_name
                   )
        )
        row = result.first()

        return row[0], row[1]

    async def update_bear_and_bull_of_selected_industry_of_current_user(
            self,
            industry_name: str,
            current_user_id: UUID,
            new_bear_factors: str,
            new_bull_factors: str
    ):

        result = await self.db.execute(
            select(Industry)
            .where(Industry.user_id == current_user_id,
                   Industry.industry_name == industry_name
                   )
        )
        industry = result.scalars().first()

        if not industry:
            return False

        industry.bear_factors = new_bear_factors
        industry.bull_factors = new_bull_factors

        await self.db.commit()

        await self.db.refresh(industry)

        return True



