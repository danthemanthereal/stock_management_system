from src.ai_metric_analysis_component.ai_metric_analysis import AIMetricAnalysisComponent
from src.prompt_loader_component.prompt_loader import PromptLoader
import re
import json
from groq import Groq

class WorkingCapitalAnalysis(AIMetricAnalysisComponent):

    def __init__(self,
                 model_name: str,
                 api_key: str,
                 user_prompt_path: str,
                 system_prompt_path: str):
        super().__init__()
        self.model_name = model_name
        self.api_key = api_key
        self.user_prompt_path = user_prompt_path
        self.system_prompt_path = system_prompt_path
        self.prompt_loader = PromptLoader()

    def analyse_financial_metrics(self,
                                  satisfied_by_category: dict,
                                  unsatisfied_by_category: dict,
                                  satisfied_only_reference_value: dict,
                                  unsatisfied_only_reference_value: dict,
                                  satisfied_only_development: dict,
                                  unsatisfied_only_development: dict,
                                  ):

        system_prompt = self.prompt_loader.load_prompt(self.system_prompt_path)

        user_prompt = self.prompt_loader.load_prompt(self.user_prompt_path)

        client = Groq(api_key=self.api_key,)

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
        return cleand_json_answer.get("evaluation", "")

    def extract_json_from_llm_output(self, text: str):

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

    def _fix_common_json_issues(self, json_str: str) -> str:

        json_str = re.sub(r",\s*}", "}", json_str)
        json_str = re.sub(r",\s*]", "]", json_str)

        json_str = re.sub(r"(?<!\\)'", '"', json_str)

        return json_str