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
            system_instruction="You are an expert of summarazing text of companies based on strengths and weakness."
        )
    )

    answer = ""
    for each in response.candidates[0].content.parts:
        answer += each.text
    return answer


def get_summary_of_gemini_of_transcript(transcript: str):
    client = genai.Client(api_key="AIzaSyDlDOLI8jYT4u_kauJ5C6x_rYSQ8q3unZU")

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Give the strength and weakness of the companies based on {transcript}."
                 f"Answer only in german."
    )
    print(response.text)
    return response.text


def get_user_prompt_url_context(url: str):
    return f"""

"""


def get_system_instruction_url_context() -> str:
    return """
<role>
You are an expert in analyzing companies based on information from provided URLs.

Your task is to identify and summarize strengths and weaknesses of each company:
- Strengths are factors that could positively impact the company's stock price.
- Weaknesses are factors that could negatively impact the company's stock price.

You must respond ONLY in German.

Your output MUST be a valid JSON array.
Do not include any explanations, comments, or additional text outside the JSON.
</role>

<instructions>
1. Analyze the provided URLs and identify relevant information about the company.

2. Extract strengths and weaknesses:
   - Strengths: factors that could positively impact the company's stock price
   - Weaknesses: factors that could negatively impact the company's stock price

3. Validate:
   - Ensure all points are based on the provided content
   - Avoid speculation or unsupported claims

4. Format:
   - Output ONLY a valid JSON array
   - Each entry must clearly separate "strengths" and "weaknesses"
   - Do not include any explanations, comments, or text outside the JSON
   - The response MUST be in German
</instructions>

<constraints>
Use only the content of the given URL.
</constraints>

<output_format>
Structure your response as follows:
   - Output ONLY a valid JSON array
   - Use the following structure for each company:
     {
       "company_name": "",
       "strength": "",
       "weakness": ""
     }
   - Do not include any explanations, comments, or text outside the JSON
   - The response MUST be in German
</output_format>
    """
