from pydantic import BaseModel


class FinancialMetricOverview(BaseModel):
    config_id: int
    metric_id: int
    display_name: str
    category: str
    reference_value: float
    unit: str
    should_rise: bool
    is_active: bool

    class Config:
        orm_mode = True