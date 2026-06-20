from pydantic import BaseModel

class WikiUpdate(BaseModel):
    new_text: str