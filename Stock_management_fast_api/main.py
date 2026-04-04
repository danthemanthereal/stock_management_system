from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from gemini_component.gemini_llm_component import get_summary_of_gemini_with_url_context
app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.post("/analyze")
def analyze(url: str = Form(...)):
    get_summary_of_gemini_with_url_context(url)
    return {"received_url": url}

