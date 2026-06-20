import json
import re

from google import genai
from google.genai.types import GenerateContentConfig
from groq import Groq
from src.youtube_transcript_component.yt_transcript_component import \
    YoutubeTranscriptComponent
import os
from dotenv import load_dotenv
from src.html__text_parser_component.bs4_text_parser import BS4TextParser

load_dotenv()


class StrengthWeaknessOfCompanyComponent:

    def __init__(self, groq_model_name):
        self.groq_model_name = groq_model_name

    async def get_strength_weakness_of_company(self, url: str):
        #text_extractor = TextExtractor()
        #text = text_extractor.get_website_text(url)

        bs4_text_parser = BS4TextParser()
        text = await  bs4_text_parser.get_website_text(url)
        return self.get_strength_weakness_of_url_with_groq(text)


    def get_summary_of_gemini_with_url_context(self,url: str):
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
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
        return self.analysis_of_yt_video_with_ollama(transcript)

    def get_summary_of_gemini_of_transcript(self,transcript: str):
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
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

    def analysis_of_yt_video_with_ollama(self,transcript: str):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        user_prompt = self.get_user_prompt_yt_script(transcript)
        system_prompt = self.get_system_instruction_youtube_script()
        response = client.chat.completions.create(
            model=self.groq_model_name,
            messages=[
                {"role": "system_prompt.txt",
                 "content": system_prompt
                 },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ])

        content = response.choices[0].message.content

        return self.safe_parse(content)


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
            - Do NOT use real line breaks (newline characters) inside any JSON string values. Instead, use the escaped form \n if a line break is absolutely necessary.
            - Alternatively, separate bullet points within a string using semicolons (;) or a simple space, so that each string remains a single continuous line.
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

    def safe_parse(self, content: str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                return []

        raw_json = match.group()

        def escape_control_in_strings(s):
            result = []
            in_string = False
            escape = False
            for ch in s:
                if in_string:
                    if escape:
                        result.append(ch)
                        escape = False
                    elif ch == '\\':
                        result.append(ch)
                        escape = True
                    elif ch == '"':
                        in_string = False
                        result.append(ch)
                    elif ch == '\n':
                        result.append('\\n')
                    elif ch == '\r':
                        result.append('\\r')
                    elif ch == '\t':
                        result.append('\\t')
                    else:
                        result.append(ch)
                else:
                    if ch == '"':
                        in_string = True
                    result.append(ch)
            return ''.join(result)

        fixed = escape_control_in_strings(raw_json)

        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return []


    def get_strength_weakness_of_url_with_groq(self, text: str):
           system_prompt = self.get_system_instruction_url_context()
           user_prompt = self.get_user_prompt_yt_script(text)
           client = Groq(api_key=os.getenv("GROQ_API_KEY"))
           response = client.chat.completions.create(
               model=self.groq_model_name,
               messages=[
                   {"role": "system_prompt.txt",
                    "content": system_prompt
                    },
                   {
                       "role": "user",
                       "content": user_prompt
                   }
               ])

           content = response.choices[0].message.content

           return self.safe_parse(content)

