from google import genai
from google.genai.types import Tool, GenerateContentConfig

def get_summary_of_gemini_with_url_context(url: str):
    client = genai.Client(api_key="AIzaSyDlDOLI8jYT4u_kauJ5C6x_rYSQ8q3unZU")
    model_id = "gemini-3-flash-preview"

    tools = [
        {"url_context": {}},
    ]


    response = client.models.generate_content(
        model=model_id,
        contents=f"Give the strength and weakness of the companies based on  {url}."
                 f"Answer only in german.",
        config=GenerateContentConfig(
            tools=tools,
        )
    )

    for each in response.candidates[0].content.parts:
        print(each.text)

