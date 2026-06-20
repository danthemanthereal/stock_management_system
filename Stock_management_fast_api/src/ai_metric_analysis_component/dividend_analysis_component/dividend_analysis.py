from src.ai_metric_analysis_component.ai_metric_analysis import AIMetricAnalysisComponent
from src.prompt_loader_component.prompt_loader import PromptLoader


class DividendAnalysis(AIMetricAnalysisComponent):

    def __init__(self,
                 model_name: str,
                 api_key: str,
                 user_prompt_path: str,
                 system_prmpt_path: str):
        super().__init__()
        self.model_name = model_name
        self.api_key = api_key,
        self.prompt_loader = PromptLoader()

    def analyse_financial_metrics(self,
                                  satisfied_by_category: dict,
                                  unsatisfied_by_category: dict,
                                  satisfied_only_reference_value: dict,
                                  unsatisfied_only_reference_value: dict,
                                  satisfied_only_development: dict,
                                  unsatisfied_only_development: dict,
                                  ):
        pass
