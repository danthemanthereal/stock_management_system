import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


class FinancialMetricAIEvaluator:

    def __init__(self,
                 model_name: str):
        self.model_name = model_name

    def evaluate_financial_metrics(self,
                                   satisfied_by_category,
                                   unsatisfied_by_category,
                                   satisfied_only_reference_value,
                                   unsatisfied_only_reference_value,
                                   satisfied_only_development,
                                   unsatisfied_only_development,
                                   ):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        user_prompt = self.get_user_prompt(
            satisfied_by_category=satisfied_by_category,
            unsatisfied_by_category=unsatisfied_by_category,
            satisfied_only_reference_value=satisfied_only_reference_value,
            unsatisfied_only_reference_value=unsatisfied_only_reference_value,
            satisfied_only_development=satisfied_only_development,
            unsatisfied_only_development=unsatisfied_only_development,
        )

        system_prompt = self.get_system_prompt()

        response = client.chat.completions.create(
            model=self.model_name,
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
        llm_answer = content
        cleand_json_answer = self.extract_json_from_llm_output(llm_answer)
        return  cleand_json_answer.get("evaluation", "")


    def get_user_prompt(self,
                        satisfied_by_category: dict,
                        unsatisfied_by_category: dict,
                        satisfied_only_reference_value: dict,
                        unsatisfied_only_reference_value: dict,
                        satisfied_only_development: dict,
                        unsatisfied_only_development: dict,
                        ):
        return f"""
Analyze the following financial KPI data.

Input consists of multiple category dictionaries:

satisfied_by_category:
{satisfied_by_category}

unsatisfied_by_category:
{unsatisfied_by_category}

satisfied_only_reference_value:
{satisfied_only_reference_value}

unsatisfied_only_reference_value:
{unsatisfied_only_reference_value}

satisfied_only_development:
{satisfied_only_development}

unsatisfied_only_development:
{unsatisfied_only_development}

TASKS:
1. Evaluate each category
2. Compare target achievement vs trend direction
3. Identify positive and negative insights
4. Detect relationships between metrics
5. Produce a final financial assessment

OUTPUT REQUIREMENT:
Return ONLY a JSON object with the following structure:
"""

    def get_system_prompt(self):
        return """
OUTPUT RULES (STRICT):

- You MUST return ONLY a valid JSON object.
- No markdown, no code fences, no explanations.
- The JSON MUST exactly match the structure below.
- Do NOT add, remove, rename or reorder keys.

Return ONLY a valid JSON object.

The JSON must have exactly this structure:

{
  "evaluation": "..."
}

Rules:
- evaluation contains a complete financial analysis as a structured text
- include:
  - category summaries
  - metric insights
  - cross-metric relationships
  - overall conclusion
- output must be in German
- no additional keys
- no markdown
- no code fences
- answer only in german
"""

    def extract_json_from_llm_output(self,text: str):


        if not text:
            raise ValueError("Empty LLM response")

        text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)

            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                cleaned = self._fix_common_json_issues(json_str)
                return json.loads(cleaned)

        raise ValueError("No valid JSON found in LLM output")

    def _fix_common_json_issues(self,json_str: str) -> str:


        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)

        json_str = re.sub(r"(?<!\\)'", '"', json_str)

        return json_str
