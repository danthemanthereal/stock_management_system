from fastapi import APIRouter, Request, Depends, BackgroundTasks, Form
from src.database import db
from src.database.models import User
from fastapi.templating import Jinja2Templates
from src.database.db import get_db
import json
from starlette.responses import HTMLResponse
from src.summary_llm_component.gemini_llm_component import \
    get_summary_of_gemini_with_url_context
from src.summary_llm_component.gemini_llm_component import get_summary_of_gemini_of_transcript
from src.youtube_transcript_component.yt_transcript_component import get_summary_of_yt_video

templates = Jinja2Templates(directory="templates")

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])

@analysis_router.get("/")
def analysis(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="analysis.html",
        context={"request": request})


@analysis_router.post("/get-summary-url", response_class=HTMLResponse)
async def analyze_url(request: Request, url: str = Form(...)):
    try:
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
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request},
        )

@analysis_router.post("/get-summary-by-yt-video", response_class=HTMLResponse)
def get_yt_transcript(request: Request, url: str = Form(...)):
    try:

        transcript = get_summary_of_yt_video(url)
        companies_array = get_summary_of_gemini_of_transcript(transcript)

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
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request},
        )