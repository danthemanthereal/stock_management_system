from youtube_transcript_api import YouTubeTranscriptApi


def get_youtube_transcript_based_url(video_id: str):
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=["de", "en"])

    transcript_text = ""
    for snippet in transcript:
        transcript_text += snippet.text
    return transcript_text