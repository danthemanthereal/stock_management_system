from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract



def get_summary_of_yt_video(url:str):
    video_id = extract_video_id_by_url(url)
    return get_youtube_transcript_based_url(video_id)

def extract_video_id_by_url(url: str) -> str:
    try:
        return extract.video_id(url)
    except Exception as e:
        return ""

def get_youtube_transcript_based_url(video_id: str):
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=["de", "en"])

    transcript_text = ""
    for snippet in transcript:
        transcript_text += snippet.text
    return transcript_text

