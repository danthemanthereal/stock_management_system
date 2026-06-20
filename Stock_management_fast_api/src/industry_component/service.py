from sqlalchemy.ext.asyncio import AsyncSession


class IndustryService:

    def __init__(self, db: AsyncSession):
        self.db = db



    def get_industry_wiki_page_of_current_user(self, industry_id: int):