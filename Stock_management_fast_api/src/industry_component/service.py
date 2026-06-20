from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Industry


class IndustryService:
    def __init__(self, db: AsyncSession):
        self.db = db



    async def get_industry_wiki_page_of_current_user(self,
                                               current_user_id: UUID
                                               ):
        result = await self.db.execute(
            select(Industry.wiki_page)
            .where(Industry.user_id == current_user_id)
        )

        rows = result.scalars().all()
        return list(rows)
