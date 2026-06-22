from app.domain.shared.base.enum import PestSenseEnum

class ObservationQuality(PestSenseEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class DataQuality(PestSenseEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    MISSING = "missing"
    SUSPECTED_ANOMALY = "suspected_anomaly"