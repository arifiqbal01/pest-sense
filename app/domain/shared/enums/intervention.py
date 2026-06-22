
from app.domain.shared.base.enum import PestSenseEnum

class InterventionType(PestSenseEnum):
    SCOUTING = "scouting"
    CULTURAL_CONTROL = "cultural_control"
    BIOLOGICAL_CONTROL = "biological_control"
    CHEMICAL_CONTROL = "chemical_control"
    MECHANICAL_CONTROL = "mechanical_control"
    MONITOR_ONLY = "monitor_only"
    NO_ACTION = "no_action"


class TreatmentStatus(PestSenseEnum):
    PLANNED = "planned"
    APPLIED = "applied"
    DELAYED = "delayed"
    FAILED = "failed"
    COMPLETED = "completed"


class RecommendationStatus(PestSenseEnum):
    GENERATED = "generated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"