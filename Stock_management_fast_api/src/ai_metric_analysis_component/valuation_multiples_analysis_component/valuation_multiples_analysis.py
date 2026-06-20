from src.ai_metric_analysis_component.ai_metric_analysis import AIMetricAnalysisComponent


class EvaluationMultiplesAnalysis(AIMetricAnalysisComponent):

    def __init__(self,
                 model_name: str,
                 api_key: str,
                 user_prompt_path: str,
                 system_prmpt_path: str
                 ):
        super().__init__()
        self.model_name = model_name
        self.api_key = api_key

    def analyse_financial_metrics(self, all_to_considered_financial_metrics):
        pass