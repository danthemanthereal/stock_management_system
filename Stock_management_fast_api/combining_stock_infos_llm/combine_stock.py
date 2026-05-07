from groq import Groq
import json
import re

def safe_parse(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"strengths": [], "weaknesses": []}


def get_combination(current_strengths, current_weakness, new_strengths, new_weakness):
    api_key = "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"
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
            You are a business analysis AI.
            Answer only in german.
            Your task is to merge two datasets about a company:
            - current strengths and weaknesses
            - new strengths and weaknesses

            GOALS:
            1. Combine both datasets into a single consistent overview.
            2. Remove duplicates or semantically identical points.
            3. Merge similar ideas into one clear statement when appropriate.
            4. Preserve all meaningful information (nothing should be lost).
            5. Keep the output concise, structured, and professional.

            IMPORTANT RULES:
            - Do NOT add explanations.
            - Do NOT include comments or analysis text.
            - Do NOT format as Markdown.

            OUTPUT FORMAT (STRICT):
            Return ONLY valid JSON:

            {
              "strengths": ["...merged strengths..."],
              "weaknesses": ["...merged weaknesses..."]
            }
            """
            }
            ,
            {
                "role": "user",
                "content": f"""
    Combine the following company data into a single consolidated analysis:
    Answer only in german. 
    
    CURRENT STRENGTHS:
    {current_strengths}

    CURRENT WEAKNESSES:
    {current_weakness}

    NEW STRENGTHS:
    {new_strengths}

    NEW WEAKNESSES:
    {new_weakness}

    Ensure all information is merged, deduplicated, and consistently structured.
    """
            }
        ]
    )

    content = response.choices[0].message.content
    data = safe_parse(content)
    strengths = data.get("strengths", [])
    weaknesses = data.get("weaknesses", [])

    return strengths, weaknesses
