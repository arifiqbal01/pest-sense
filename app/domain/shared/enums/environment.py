

from app.domain.shared.base.enum import PestSenseEnum
class EnvironmentType(PestSenseEnum):
    OPEN_FIELD = "open_field"
    OPEN_FIELD_IRRIGATED_AGRICULTURE = "open_field_irrigated_agriculture"
    GREENHOUSE = "greenhouse"
    TUNNEL = "tunnel"
    NET_HOUSE = "net_house"


class ClimateZone(PestSenseEnum):
    ARID = "arid"
    SEMI_ARID = "semi_arid"
    TROPICAL = "tropical"
    SUBTROPICAL = "subtropical"
    TEMPERATE = "temperate"
    HOT_DESERT_BWH = "hot_desert_bwh"


class RainfallDistribution(PestSenseEnum):
    EVEN = "even"
    SEASONAL = "seasonal"
    HIGHLY_SEASONAL_LOW_TOTAL = "highly_seasonal_low_total"


class MonsoonInfluence(PestSenseEnum):
    NONE = "none"
    WEAK = "weak"
    WEAK_TO_MODERATE = "weak_to_moderate"
    MODERATE = "moderate"
    STRONG = "strong"


class WeatherResolution(PestSenseEnum):
    FARM = "farm_level"
    VILLAGE = "village_level"
    TEHSIL = "tehsil_level"
    DISTRICT = "district_level"


class CroppingSystem(PestSenseEnum):
    IRRIGATED_COTTON = "irrigated_cotton"
    RAINFED = "rainfed"
    MIXED_CROPPING = "mixed_cropping"
    GREENHOUSE_PRODUCTION = "greenhouse_production"


class EnvironmentalEventType(PestSenseEnum):
    HEATWAVE = "heatwave"
    DROUGHT = "drought"
    PROLONGED_HUMIDITY = "prolonged_humidity"
    HEAVY_RAINFALL = "heavy_rainfall"
    COLD_STRESS = "cold_stress"
    RAPID_TEMPERATURE_DROP = "rapid_temperature_drop"
    UNSEASONAL_RAINFALL = "unseasonal_rainfall"
    DUST_STORM = "dust_storm"