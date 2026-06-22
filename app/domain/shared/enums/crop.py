from app.domain.shared.base.enum import PestSenseEnum


class CropStageType(PestSenseEnum):
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    BOLL_FORMATION = "boll_formation"
    MATURITY = "maturity"
    HARVEST_READY = "harvest_ready"