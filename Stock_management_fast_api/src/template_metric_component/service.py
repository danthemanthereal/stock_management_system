from sqlalchemy.orm import Session
from src.database.models import ProfileMetricConfiguration


class TemplateMetricService:
    def __init__(self, db: Session):
        self.db = db


    def update_template_metric_configuration(self, config_id, new_reference_value: int, should_rise: bool, is_active: bool):
        try:
            current_config = self.db.query(ProfileMetricConfiguration).filter(ProfileMetricConfiguration.id == config_id).first()

            if current_config:
                current_config.should_rise = should_rise
                current_config.is_active = is_active
                current_config.reference_value = new_reference_value
                self.db.commit()
                self.db.refresh(current_config)
                return True
            return False
        except Exception as e:
            print(e)
            return False


    def get_config_by_metric_and_template_id(self, metric_id: int, template_id: int):
        return self.db.query(ProfileMetricConfiguration).filter(
            ProfileMetricConfiguration.metric_id == metric_id,
            ProfileMetricConfiguration.profile_id == template_id
        ).first()
