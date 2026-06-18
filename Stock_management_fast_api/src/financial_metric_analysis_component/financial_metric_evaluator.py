from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import FinancialMetric, ProfileMetricConfiguration
from src.template_component.service import TemplateService
from src.template_metric_component.service import TemplateMetricService

from src.financial_metric_analysis_component.utils import \
    group_financial_metrics_map_by_category, group_metric_names_by_category, build_category_pair_summary



class FinancialMetricEvaluator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_satisfied_unsatisfied_by_category_and_summary(self,
                                                          all_to_considered_financial_metrics:dict,
                                                          current_user_id: UUID):
        (satisfied_metrics, unsatisfied_metrics,
         satisfied_benchmarks, unsatisfied_benchmarks,
         satisfied_development, unsatisfied_development) = await  self.get_satisfied_and_not_satisfied_financial_metrics(all_to_considered_financial_metrics,current_user_id)

        data_by_category = await group_financial_metrics_map_by_category(
                all_to_considered_financial_metrics,self.db)


        satisfied_metrics_by_category = await group_metric_names_by_category(
              satisfied_metrics, self.db
        )
        unsatisfied_metrics_by_category = await group_metric_names_by_category(
              unsatisfied_metrics, self.db
          )
        satisfied_benchmarks_by_category = await group_metric_names_by_category(
             satisfied_benchmarks, self.db
        )

        unsatisfied_benchmarks_by_category = await group_metric_names_by_category(
             unsatisfied_benchmarks, self.db
        )
        satisfied_development_by_category = await group_metric_names_by_category(
          satisfied_development, self.db
        )                                   
        unsatisfied_development_by_category = await group_metric_names_by_category(
         unsatisfied_development, self.db
        )

        summary_combined = build_category_pair_summary(
        satisfied_metrics_by_category,
        unsatisfied_metrics_by_category,
        )
        summary_benchmark = build_category_pair_summary(
                satisfied_benchmarks_by_category,
                unsatisfied_benchmarks_by_category,
        )

        summary_development = build_category_pair_summary(
             satisfied_development_by_category,
             unsatisfied_development_by_category,
         )

        return (data_by_category, satisfied_metrics_by_category, unsatisfied_metrics_by_category,
                satisfied_benchmarks_by_category, unsatisfied_benchmarks_by_category,
                satisfied_development_by_category, unsatisfied_development_by_category,
                summary_combined, summary_benchmark, summary_development)


    async def get_satisfied_and_not_satisfied_financial_metrics(self, financial_metrics: dict, current_user_id: UUID):
        satisfied_financial_metrics = []
        unsatisfied_financial_metrics = []
        satisfied_development_metric = []
        unsatisfied_development_metric = []
        satisfied_benchmark_value = []
        unsatisfied_benchmark_value = []
        template_metric_service = TemplateMetricService(self.db)
        template_service = TemplateService(self.db)
        current_used_template_id = await template_service.get_last_selected_template_id_of_user(current_user_id)
        from src.financial_metric_analysis_component.financial_metric_service import MetricsService

        financial_metric_service = MetricsService(self.db)
        for financial_metric_name in financial_metrics.keys():
            values = financial_metrics[financial_metric_name]
            financial_metric_id = await financial_metric_service.get_id_of_current_metric_by_name(financial_metric_name)
            if await template_metric_service.check_if_current_user_activated_this_metric_in_current_template(
                    current_used_template_id,
                    financial_metric_id
            ) and values:

                if any(isinstance(x, str) for x in values):
                    continue

                profile_metric_config_object, financial_metric_object = await template_metric_service.get_financial_metric_config_and_financial_metric_objects(
                    financial_metric_name, current_used_template_id
                )

                possible_result_satisfiability = self.check_satisfiability(financial_metric_object, profile_metric_config_object, values)
                possible_result_development_only = self.check_satisfiability_development(profile_metric_config_object,
                                                                                         values)
                possible_result_benchmark_only = self.check_satisfiability_benchmark_value(financial_metric_object,
                                                                                           profile_metric_config_object,
                                                                                           values)

                if not possible_result_satisfiability or not possible_result_development_only or not possible_result_benchmark_only:
                    continue

                if possible_result_satisfiability:
                    satisfied_financial_metrics.append(financial_metric_name)
                else:
                    unsatisfied_financial_metrics.append(financial_metric_name)

                if possible_result_development_only:
                    satisfied_development_metric.append(financial_metric_name)
                else:
                    unsatisfied_development_metric.append(financial_metric_name)

                if possible_result_benchmark_only:
                    satisfied_benchmark_value.append(financial_metric_name)
                else:
                    unsatisfied_benchmark_value.append(financial_metric_name)

        return (satisfied_financial_metrics, unsatisfied_financial_metrics,
                satisfied_benchmark_value, unsatisfied_benchmark_value,
                satisfied_development_metric, unsatisfied_development_metric)

    def check_satisfiability(self, financial_metric_obj: FinancialMetric,
                             profile_metric_config_object: ProfileMetricConfiguration,
                             values: list[int]) -> bool | None:
        try:
            last_value = values[-1]
            if financial_metric_obj.unit == "%":
                last_value = int(last_value * 100)

            if profile_metric_config_object.should_rise:
                asc_sorting = sorted(values)

                return asc_sorting == values and profile_metric_config_object.reference_value > last_value
            else:
                desc_sorting = sorted(values, reverse=True)
                return desc_sorting == values and last_value < profile_metric_config_object.reference_value
        except Exception as e:
            print(e)
            print(f"error in value ", values)
            print(f"fin metic obj {profile_metric_config_object}")
            return None

    def check_satisfiability_development(self, financial_metric_config_obj: ProfileMetricConfiguration,
                                         values: list[int]) -> bool | None:
        try:
            if financial_metric_config_obj.should_rise:
                asc_sorting = sorted(values)

                return asc_sorting == values
            else:
                desc_sorting = sorted(values, reverse=True)
                return desc_sorting == values
        except Exception as e:
            print(e)
            print(f"error in value ", values)
            print(f"fin metic obj {financial_metric_config_obj}")
            return None

    def check_satisfiability_benchmark_value(self, financial_metric_obj: FinancialMetric, profile_metric_config_object,
                                             values: list[int]) -> bool | None:
        try:
            last_value = values[-1]
            if financial_metric_obj.unit == "%":
                last_value = int(last_value * 100)

            if profile_metric_config_object.should_rise:

                return profile_metric_config_object.reference_value > last_value
            else:
                return profile_metric_config_object.reference_value < last_value
        except Exception as e:
            print(e)
            print(f"error in value ", values)
            print(f"fin metic obj {profile_metric_config_object}")
            return None
