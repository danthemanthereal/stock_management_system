from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import FinancialMetric, User, IndustryProfile
from src.database.db import get_db



def get_available_metrics(db: Session) -> List[FinancialMetric]:
    return db.query(FinancialMetric).order_by(FinancialMetric.name).all()

def get_last_selected_template_id_of_user(current_user_id: UUID, db: Session)->int:
    if not check_if_user_already_has_template(db,current_user_id):
        over_all_user_template = IndustryProfile(
            name="Allgemein",
            user_id=str(current_user_id)
        )
        db.add(over_all_user_template)
        db.commit()
        db.refresh(over_all_user_template)
        return set_to_current_user_his_first_template(db,current_user_id, over_all_user_template.id)

    return get_last_selected_template_id_if_user(current_user_id, db)



def check_if_user_already_has_template(db: Session, user_id: UUID)->bool:
    return db.query(User).filter_by(id = user_id).first().last_selected_template_id is not None


def set_to_current_user_his_first_template(db: Session, user_id: UUID, template_id: int) -> int:
    current_user = db.query(User).filter_by(id=user_id).first()
    current_user.last_selected_template_id = template_id
    db.commit()
    db.refresh(current_user)
    return current_user.last_selected_template_id

def get_last_selected_template_id_if_user(current_user_id: UUID, db: Session)->int:
    return db.query(User).filter_by(id=current_user_id).first().last_selected_template_id

def get_current_user_created_templates(db: Session, user_id: UUID)->List[IndustryProfile]:
    return db.query(IndustryProfile).filter(IndustryProfile.user_id == str(user_id)).all()

