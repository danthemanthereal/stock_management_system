from groq import Groq
import re
import json

def safe_parse(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"strengths": [], "weaknesses": []}

def evaluate_new_information(current_strengths,
                             new_strengths,
                             current_weaknesses,
                             new_weaknesses):
    api_key = "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"
    client = Groq(api_key=api_key)
    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(current_strengths, new_strengths, current_weaknesses, new_weaknesses)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system",
                "content": system_prompt
             },
            {
                "role": "user",
                "content": user_prompt
            }
        ])

    content = response.choices[0].message.content
    data = safe_parse(content)
    trajectory = data.get("trajectory", "")
    reasoning = data.get("reasoning", "")
    recommendation = data.get("recommendation", "")

    return trajectory, reasoning, recommendation


def get_system_prompt() -> str:
    return """
    <role>
    You are an expert corporate strategist and financial analyst specializing in risk assessment and company evaluations.
    </role>

    <context>
    You will be provided with:
    1. The Current Strengths and Current Weaknesses of a specific company.
    2. The New Strengths and New Weaknesses that have recently emerged.
    </context>

    <instructions>
    Your task is to analyze how the newly emerged information impacts the company's overall situation. 

    Follow these analytical steps:
    1. Assess the New Strengths: Do they successfully mitigate or neutralize the current weaknesses?
    2. Assess the New Weaknesses: How severely do they damage the company or undermine its existing strengths?
    3. Determine the Trajectory: Based on the shift from current to new, has the overall situation Improved, Worsened, or remained Unchanged?
    4. Answer only in German. 

    CRITICAL CONSTRAINTS:
    - You MUST base your entire analysis, reasoning, and recommendation STRICTLY on the provided context. 
    - DO NOT hallucinate, assume facts, or use outside knowledge about the company.
    - Your output MUST be ONLY a valid, parseable JSON object. Do not include any markdown formatting (like ```json), preambles, or concluding remarks.
    </instructions>

    <output_format>
    {
      "trajectory": "State exactly one of: 'Improved', 'Worsened', 'Unchanged'",
      "reasoning": "Explain clearly why the situation changed, referencing the provided strengths and weaknesses.",
      "recommendation": "Provide a brief recommendation based solely on the provided data."
    }
    </output_format>
    """


def get_user_prompt(current_strengths: str,
                    new_strengths: str,
                    current_weaknesses: str,
                    new_weaknesses: str) -> str:
    return f"""
    Please analyze the following company data and provide the evaluation in the requested JSON format.

    <current_strengths>
    {current_strengths}
    </current_strengths>

    <current_weaknesses>
    {current_weaknesses}
    </current_weaknesses>

    <new_strengths>
    {new_strengths}
    </new_strengths>

    <new_weaknesses>
    {new_weaknesses}
    </new_weaknesses>
    """
