from sqlalchemy.orm import Session


class LLMWiki:

    def __init__(self, db: Session):
        pass

    def find_relevant_companies_information(self, ticker: str):
        current_strengths = ""
        current_weaknesses = ""
