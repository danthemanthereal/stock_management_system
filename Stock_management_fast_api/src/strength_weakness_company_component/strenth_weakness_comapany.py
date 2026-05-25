from google import genai
from google.genai.types import GenerateContentConfig
from src.youtube_transcript_component.yt_transcript_component import \
    YoutubeTranscriptComponent


class StrengthWeaknessOfCompanyComponent:

    def get_strength_weakness_of_company(self, url):
        return self.get_summary_of_gemini_with_url_context(url)


    def get_summary_of_gemini_with_url_context(self,url: str):
        client = genai.Client(api_key="AIzaSyDlDOLI8jYT4u_kauJ5C6x_rYSQ8q3unZU")
        model_id = "gemini-3-flash-preview"

        tools = [
            {"url_context": {}},
        ]

        system_prompt = self.get_system_instruction_url_context()
        user_prompt = self.get_user_prompt_url_context(url)
        response = client.models.generate_content(
            model=model_id,
            contents=user_prompt,
            config=GenerateContentConfig(
                tools=tools,
                system_instruction=system_prompt
            )
        )

        answer = ""
        for each in response.candidates[0].content.parts:
            answer += each.text
        return answer

    def get_strength_weakness_of_youtube(self,url:str):
        transcript_component = YoutubeTranscriptComponent()
        transcript = transcript_component.get_summary_of_yt_video(url)
        return self.get_summary_of_gemini_of_transcript(transcript)

    def get_summary_of_gemini_of_transcript(self,transcript: str):
        client = genai.Client(api_key="AIzaSyDlDOLI8jYT4u_kauJ5C6x_rYSQ8q3unZU")
        user_prompt = self.get_user_prompt_yt_script(transcript)
        system_prompt = self.get_system_instruction_youtube_script()
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=user_prompt,
            config=GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        return response.text


    def get_user_prompt_url_context(self,url: str):
        return f"""
    <context>
    URL: {url}
    </context>
    
    <task>
    Analyze the content of the provided URL and identify all relevant companies.
    
    For each identified company:
    - Provide a brief summary of the company.
    - Identify strengths (factors that could positively impact the company's stock price).
    - Identify weaknesses (factors that could negatively impact the company's stock price).
    
    Use only information from the provided URL. Do not speculate or add unsupported claims.
    </task>
    
    <output_format>
    Return ONLY a valid JSON array.
    
    Use the exact following structure for each company:
    [
      {{
        "company_name": "Company name",
        "strength": "• Factor 1\n• Factor 2",
        "weakness": "• Factor 1\n• Factor 2"
      }}
    ]
    
    Rules:
    - The response MUST be in German
    - Do not include any explanations or comments outside the JSON
    - Use double quotes only (strict JSON)
    - No trailing commas
    - If no companies are found, return an empty array []
    </output_format>
    """

    def get_user_prompt_yt_script(self,script: str):

        return f"""
        <context>
        text: {script}
        </context>
    
        <task>
        Analyze the content of the provided text and identify all relevant companies.
    
        For each identified company:
        - Provide a brief summary of the company.
        - Identify strengths (factors that could positively impact the company's stock price).
        - Identify weaknesses (factors that could negatively impact the company's stock price).
    
        Use only information from the provided text. Do not speculate or add unsupported claims.
        </task>
    
        <output_format>
        Return ONLY a valid JSON array.
    
        Use the exact following structure for each company:
        [
          {{
            "company_name": "Company name",
            "strength": "• Factor 1\n• Factor 2",
            "weakness": "• Factor 1\n• Factor 2"
          }}
        ]
    
        Rules:
        - The response MUST be in German
        - Do not include any explanations or comments outside the JSON
        - Use double quotes only (strict JSON)
        - No trailing commas
        - If no companies are found, return an empty array []
        </output_format>
        """

    def get_system_instruction_url_context(self) -> str:
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


    def get_system_instruction_youtube_script(self) -> str:
        return """
    <role>
    You are an expert in analyzing companies based on information from provided text.
    
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
    Use only the content of the given text.
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