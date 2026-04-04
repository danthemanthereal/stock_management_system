from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

from youtube_transcript_component.yt_transcript_component import \
    get_youtube_transcript_based_url
from gemini_component.gemini_llm_component import get_summary_of_gemini_with_url_context, \
    get_summary_of_gemini_of_transcript

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.post("/get-summary")
def analyze(url: str = Form(...)):
    get_summary_of_gemini_with_url_context(url)
    return {"received_url": url}


@app.post("/get-yt-transcript")
def get_yt_transcript(video_id: str = Form(...)):
    transcript = get_youtube_transcript_based_url(video_id)
    get_summary_of_gemini_of_transcript(transcript)
    return {"received_url": video_id}

