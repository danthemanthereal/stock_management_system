import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from src.database.models import IndustryProfile, ProfileMetricConfiguration, User




class TemplateService:
    def __init__(self, db: Session):
        self.db = db

    def create_template_from_active_metrics(
        self,
        user_id: uuid.UUID,
        new_profile_name: str,
        triplets_str: Optional[str]
    ) -> int:

        new_template = IndustryProfile(
            name=new_profile_name,
            user_id=str(user_id)
        )
        self.db.add(new_template)
        self.db.commit()
        self.db.refresh(new_template)

        if triplets_str:
            for item in triplets_str.split(","):
                parts = item.strip().split("|")
                if len(parts) < 4:
                    continue
                metric_id = int(parts[0])
                reference_value = float(parts[1])

                should_rise = parts[3].lower() == "true"

                new_cfg = ProfileMetricConfiguration(
                    profile_id=new_template.id,
                    metric_id=metric_id,
                    reference_value=reference_value,
                    should_rise=should_rise,
                    is_active=True
                )
                self.db.add(new_cfg)
                self.db.commit()
                self.db.refresh(new_cfg)

        self.update_last_selected_template_id(new_template.id,user_id)
        return new_template.id

    def get_last_selected_template_id_of_user(self, current_user_id: uuid.UUID) -> int:
        if not self.check_if_user_already_has_template(current_user_id):
            over_all_user_template = IndustryProfile(
                name="Allgemein",
                user_id=str(current_user_id)
            )
            db.add(over_all_user_template)
            db.commit()
            db.refresh(over_all_user_template)
            return self.set_to_current_user_his_first_template(current_user_id, over_all_user_template.id)

        return self.get_last_selected_template_id_if_user(current_user_id)

    def check_if_user_already_has_template(self, user_id: uuid.UUID) -> bool:
        return self.db.query(User).filter_by(id=user_id).first().last_selected_template_id is not None

    def set_to_current_user_his_first_template(self, user_id: uuid.UUID, template_id: int) -> int:
        current_user = self.db.query(User).filter_by(id=user_id).first()
        current_user.last_selected_template_id = template_id
        self.db.commit()
        self.db.refresh(current_user)
        return current_user.last_selected_template_id

    def get_last_selected_template_id_if_user(self, current_user_id: uuid.UUID) -> int:
        return self.db.query(User).filter_by(id=current_user_id).first().last_selected_template_id

    def get_current_user_created_templates(self,user_id: uuid.UUID) -> List[IndustryProfile]:
        return self.db.query(IndustryProfile).filter(IndustryProfile.user_id == str(user_id)).all()

    def update_last_selected_template_id(self, template_id: int, user_id: uuid.UUID):
        current_user = self.db.query(User).filter(User.id == user_id).first()
        current_user.last_selected_template_id = template_id
        self.db.commit()
        self.db.refresh(current_user)