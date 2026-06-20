import json
import re
from dotenv import load_dotenv
import os
from src.ai_metric_analysis_component.capital_cost_analysis_component.capital_cost_analysis import CapitalCostAnalysis
from src.ai_metric_analysis_component.dividend_analysis_component.dividend_analysis import DividendAnalysis
from src.ai_metric_analysis_component.expense_ratio_analysis_component.expense_ratio_analysis import \
    ExpenseRatioAnalysisComponent
from src.ai_metric_analysis_component.financial_stability_analysis_component.financial_stability_analysis import \
    FinancialStabilityAnalysisComponent
from src.ai_metric_analysis_component.profibility_analysis_component.profitability_analysis import ProfitabilityAnalysis
from src.ai_metric_analysis_component.score_analysis_component.score_analysis import ScoreAnalysis
from src.ai_metric_analysis_component.structure_analysis_component.structure_analysis import StructureAnalysis
from src.ai_metric_analysis_component.utils import get_all_considered_category_of_current_request
from src.ai_metric_analysis_component.valuation_multiples_analysis_component.valuation_multiples_analysis import \
    EvaluationMultiplesAnalysis
from src.ai_metric_analysis_component.working_capital_analysis_component.working_capital_analysis import \
    WorkingCapitalAnalysis

load_dotenv()


class FinancialMetricAIEvaluator:

    def __init__(self,
                 model_name: str):
        self.model_name = model_name
        self.analysis_components = {
            "Aufwandsquote":ExpenseRatioAnalysisComponent(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/capital_cost_user.txt",
                system_prmpt_path="prompts/capital_cost_system.txt"
            ),
            "Working Capital Management": WorkingCapitalAnalysis(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/profitability_user.txt",
                system_prmpt_path="prompts/profitability_system.txt"
            ),
            "Finanzielle Stabilität": FinancialStabilityAnalysisComponent(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/valuation_user.txt",
                system_prmpt_path="prompts/valuation_system.txt"
            ),
            "Score": ScoreAnalysis(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/expense_user.txt",
                system_prmpt_path="prompts/expense_system.txt"
            ),
            "Dividende": DividendAnalysis(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/expense_user.txt",
                system_prmpt_path="prompts/expense_system.txt"
            ),
            "Rentabilität": ProfitabilityAnalysis(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/expense_user.txt",
                system_prmpt_path="prompts/expense_system.txt"
            ),
            "Bewertungskennzahl": EvaluationMultiplesAnalysis(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/expense_user.txt",
                system_prmpt_path="prompts/expense_system.txt"
            ),
            "(Kapital)Struktur": StructureAnalysis(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/expense_user.txt",
                system_prmpt_path="prompts/expense_system.txt"
            ),
            "Kapitalkosten": CapitalCostAnalysis(
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                user_prompt_path="prompts/expense_user.txt",
                system_prmpt_path="prompts/expense_system.txt"
            ),
        }

    def evaluate_financial_metrics(self,
                                   satisfied_by_category,
                                   unsatisfied_by_category,
                                   satisfied_only_reference_value,
                                   unsatisfied_only_reference_value,
                                   satisfied_only_development,
                                   unsatisfied_only_development,
                                   ):

        print("satisfield one map ")
        print(satisfied_by_category)

        current_all_considered_categories = get_all_considered_category_of_current_request(
            satisfied_by_category_map=satisfied_by_category
        )

        total_ai_evaluation = ""

        for category in current_all_considered_categories:
            current_category_analysis = self.get_ai_evaluation_capital_per_category(
                category_name=category,
                satisfied_by_category= satisfied_by_category,
                unsatisfied_by_category=unsatisfied_by_category,
                satisfied_only_reference_value=satisfied_only_reference_value,
                unsatisfied_only_reference_value=unsatisfied_only_reference_value,
                satisfied_only_development=satisfied_only_development,
                unsatisfied_only_development=unsatisfied_only_development,

            )

            total_ai_evaluation += f"{category}: "
            total_ai_evaluation += "\n"
            total_ai_evaluation += current_category_analysis
            total_ai_evaluation += "\n"


        return total_ai_evaluation




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

    def get_ai_evaluation_capital_per_category(self,
                                       category_name: str,
                                       satisfied_by_category,
                                       unsatisfied_by_category,
                                       satisfied_only_reference_value,
                                       unsatisfied_only_reference_value,
                                       satisfied_only_development,
                                       unsatisfied_only_development,
                                       )->str:
        pass

