from src.ai_metric_analysis_component.ai_metric_analysis import AIMetricAnalysisComponent
from src.prompt_loader_component.prompt_loader import PromptLoader


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

