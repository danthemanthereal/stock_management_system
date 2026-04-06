from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from youtube_transcript_component.yt_transcript_component import \
    get_youtube_transcript_based_url
from gemini_component.gemini_llm_component import get_summary_of_gemini_with_url_context, \
    get_summary_of_gemini_of_transcript
import json
app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.post("/get-summary", response_class=HTMLResponse)
async def analyze(request: Request, url: str = Form(...)):

    companies_array = get_summary_of_gemini_with_url_context(url)

    if isinstance(companies_array, str):
        try:
            companies_array = json.loads(companies_array)
        except json.JSONDecodeError:
            companies_array = []

    return templates.TemplateResponse(
        request=request,
        name="companies_overview.html",
        context={"request": request, "companies": companies_array}
    )


@app.post("/get-yt-transcript", response_class=HTMLResponse)
def get_yt_transcript(request: Request, video_id: str = Form(...)):
    transcript = get_youtube_transcript_based_url(video_id)
    companies_array = get_summary_of_gemini_of_transcript(transcript)
    print(companies_array)
    if isinstance(companies_array, str):
        try:
            companies_array = json.loads(companies_array)
        except json.JSONDecodeError:
            companies_array = []

    return templates.TemplateResponse(
        request=request,
        name="companies_overview.html",
        context={"request": request, "companies": companies_array}
    )
