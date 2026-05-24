import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.database.models import IndustryProfile, ProfileMetricConfiguration, User



class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def add_metric_to_profile(self, profile_id: int, metric_id: int,
                              reference_value: int, should_rise: bool,
                              user_id: uuid.UUID):
        profile = self.db.query(IndustryProfile).filter(
            IndustryProfile.id == profile_id,
            IndustryProfile.user_id == str(user_id)
        ).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profil nicht gefunden")

        existing = self.db.query(ProfileMetricConfiguration).filter(
            ProfileMetricConfiguration.profile_id == profile_id,
            ProfileMetricConfiguration.metric_id == metric_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Kennzahl bereits im Profil vorhanden")

        config = ProfileMetricConfiguration(
            profile_id=profile_id,
            metric_id=metric_id,
            reference_value=reference_value,
            should_rise=should_rise,
            is_active=True
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)


    def update_last_selected_template_id(self, template_id: int, user_id: uuid.UUID):
        current_user = self.db.query(User).filter(User.id == user_id).first()
        current_user.last_selected_template_id = template_id
        self.db.commit()
        self.db.refresh(current_user)