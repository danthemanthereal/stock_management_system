import json
import re
from dotenv import load_dotenv
import os
from groq import Groq
from src.ai_financial_metricevaluation_component.utils import get_all_used_categories_for_eval, \
    get_each_metrics_list_by_category

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

        print("satisfield one map ")
        print(satisfied_by_category)

        current_all_considered_categories = get_all_used_categories_for_eval(
            category_satisfied_map=satisfied_by_category
        )

        total_ai_evaluation = ""

        for category in current_all_considered_categories:

            (satisfied_current_category,
             unsatisfied_current_category,
             satisfied_only_reference_value_current_category,
             unsatisfied_only_reference_value_current_category,
             satisfied_only_development_current_category,
             unsatisfied_only_development_current_category,
             ) = get_each_metrics_list_by_category(category=category,
                                                   category_satisfied_map=satisfied_by_category,
                                                   category_unsatisfied_map=unsatisfied_by_category,
                                                   category_satisfied_only_reference_value_map=satisfied_only_reference_value,
                                                   category_unsatisfied_only_reference_value_map=unsatisfied_only_reference_value,
                                                   category_satisfied_only_development_map=satisfied_only_development,
                                                   category_unsatisfied_development_map=unsatisfied_only_development,
                                                   )
            current_category_analysis = self.get_ai_evaluation_capital_per_category(
                category_name=category,
                satisfied_of_one_category=satisfied_current_category,
                unsatisfied_of_one_category=unsatisfied_current_category,
                satisfied_only_reference_value_of_one_category=satisfied_only_reference_value_current_category,
                unsatisfied_only_reference_value_of_one_category=unsatisfied_only_reference_value_current_category,
                satisfied_only_development_of_one_category=satisfied_only_development_current_category,
                unsatisfied_only_development_of_one_category=unsatisfied_only_development_current_category,
            )

            total_ai_evaluation += f"{category}: "
            total_ai_evaluation += "\n"
            total_ai_evaluation += current_category_analysis
            total_ai_evaluation += "\n"


        return total_ai_evaluation

    def get_user_prompt(self,
                            category_name: str,
                            satisfied_of_one_category: list[str],
                            unsatisfied_of_one_category: list[str],
                            satisfied_only_reference_value_of_one_category: list[str],
                            unsatisfied_only_reference_value_of_one_category: list[str],
                            satisfied_only_development_of_one_category: list[str],
                            unsatisfied_only_development_of_one_category: list[str],
                            ) -> str:
            return f"""
You are a financial analyst. Interpret the following pre-classified KPI data for the category: **{category_name}**.

**Context:**  
The KPIs have already been classified into 6 groups based on two criteria:
- Reference Value (RV): Does the KPI meet the target?
- Development (DEV): Does the KPI show positive improvement (e.g., vs. last year)?

---

**INPUT DATA (Pre-classified lists):**

1. **Fully Satisfied (RV ✅ & DEV ✅):**  
   {satisfied_of_one_category}

2. **Fully Unsatisfied (RV ❌ & DEV ❌):**  
   {unsatisfied_of_one_category}

3. **RV met only (RV ✅ but DEV ❌):**  
   {satisfied_only_reference_value_of_one_category}

4. **DEV met only (RV ❌ but DEV ✅):**  
   {unsatisfied_only_reference_value_of_one_category}

5. **DEV met only (RV ❌ but DEV ✅) – Logical duplicate of #4:**  
   {satisfied_only_development_of_one_category}

6. **RV met only (RV ✅ but DEV ❌) – Logical duplicate of #3:**  
   {unsatisfied_only_development_of_one_category}

---

**LOGICAL NOTE (to avoid duplication in your analysis):**
- Groups **3 and 6** are logically identical (both = RV met, DEV not met).
- Groups **4 and 5** are logically identical (both = RV not met, DEV met).
- Treat them as combined pairs for your "Trade-offs" analysis, though you may reference the raw lists if helpful.

---

**YOUR TASKS (Analyze, do NOT re-classify):**

Create a complete financial analysis text for the category "{category_name}". This text will be inserted into the `"evaluation"` JSON field (the format is enforced by the system prompt).

Your text MUST include the following structured components in coherent paragraphs:

1. **Category Summary** (1–2 sentences):  
   What is the overall state of the "{category_name}" category?

2. **Strengths (Top Performers)**:  
   Which KPIs are in the "Fully Satisfied" group? Why are they particularly strong? Provide specific examples.

3. **Critical Weaknesses (Red Flags)**:  
   Which KPIs are in the "Fully Unsatisfied" group? What risks do they pose?

4. **Trade-offs & Momentum Analysis** (Core section):  
   - KPIs that meet RV but lack development (Groups 3+6) → indicate **stability but stagnation**.  
   - KPIs that miss RV but show development (Groups 4+5) → indicate **catching up but still below target**.  
   Interpret what this tension means for the overall category.

5. **Final Verdict**:  
   Choose ONE concluding assessment for this category: `"Healthy"`, `"Stable"`, `"Caution"`, or `"Critical"`. Justify your choice in 1–2 sentences.

---

**CRITICAL OUTPUT INSTRUCTIONS (aligned with the System Prompt):**
- You generate **ONLY the raw analysis text**.
- The JSON wrapper (`{{"evaluation": "..."}}`) is automatically enforced by the system prompt – **do NOT output JSON yourself**.
- **LANGUAGE REQUIREMENT:** Even though these instructions are in English, the **actual analysis text** you produce MUST be written in **German** (as strictly required by the system prompt).
- Do NOT use bullet points or markdown lists inside the text – use clean, flowing paragraphs instead.
- Do NOT include introductory phrases like "Here is my analysis" – start directly with the summary text.

Now, generate the analysis for the category "{category_name}".
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
                                       satisfied_of_one_category: list[str],
                                       unsatisfied_of_one_category:list[str],
                                       satisfied_only_reference_value_of_one_category: list[str],
                                       unsatisfied_only_reference_value_of_one_category: list[str],
                                       satisfied_only_development_of_one_category: list[str],
                                       unsatisfied_only_development_of_one_category: list[str],
                                       )->str:

        try:

            client = Groq(api_key=os.getenv("GROQ_API_KEY"))

            system_prompt = self.get_system_prompt()

            user_prompt = self.get_user_prompt(
                category_name=category_name,
                satisfied_of_one_category=satisfied_of_one_category,
                unsatisfied_of_one_category=unsatisfied_of_one_category,
                satisfied_only_reference_value_of_one_category=satisfied_only_reference_value_of_one_category,
                unsatisfied_only_reference_value_of_one_category=unsatisfied_only_reference_value_of_one_category,
                satisfied_only_development_of_one_category=satisfied_only_development_of_one_category,
                unsatisfied_only_development_of_one_category=unsatisfied_only_development_of_one_category,
            )

            response = client.chat.completions.create(
                model=self.model_name,
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
            llm_answer = content
            cleand_json_answer = self.extract_json_from_llm_output(llm_answer)
            return cleand_json_answer.get("evaluation", "")




        except Exception as e:
            print(e)
            return ""

