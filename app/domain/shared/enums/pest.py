

from app.domain.shared.base.enum import PestSenseEnum
class OutbreakStatus(PestSenseEnum):
    DORMANT = "dormant"
    EMERGING = "emerging"
    DEVELOPING = "developing"
    ACTIVE = "active"
    PEAK = "peak"
    DECLINING = "declining"


class PestCategory(PestSenseEnum):
    INSECT = "insect"
    MITE = "mite"
    FUNGUS = "fungus"
    BACTERIA = "bacteria"
    VIRUS = "virus"
    NEMATODE = "nematode"
    WEED = "weed"


class PestLifecycleStage(PestSenseEnum):
    EGG = "egg"
    CRAWLER = "crawler"
    NYMPH = "nymph"
    NYMPH_1 = "nymph_1"
    NYMPH_2 = "nymph_2"
    NYMPH_3 = "nymph_3"
    NYMPH_4 = "nymph_4"
    LARVA = "larva"
    PREPUPA = "prepupa"
    PUPA = "pupa"
    ADULT = "adult"
    ADULT_FEMALE = "adult_female"
    ADULT_MALE = "adult_male"
    ADULT_APTEROUS_FEMALE = "adult_apterous_female"
    ADULT_ALATE_FEMALE = "adult_alate_female"


class DamageType(PestSenseEnum):
    SAP_SUCKING = "sap_sucking"
    PHLOEM_DEPLETION = "phloem_depletion"
    PHLOEM_SAP_EXTRACTION = "phloem_sap_extraction"
    SALIVARY_TOXIN_INJECTION = "salivary_toxin_injection"
    VIRUS_TRANSMISSION = "virus_transmission"

    RASPING_FEEDING = "rasping_feeding"
    LEAF_CHEWING = "leaf_chewing"
    LEAF_CURLING = "leaf_curling"
    LEAF_YELLOWING = "leaf_yellowing"
    LEAF_REDDENING = "leaf_reddening"
    LEAF_NECROSIS = "leaf_necrosis"
    LEAF_DISTORTION = "leaf_distortion"

    HOPPERBURN = "hopperburn"
    STUNTING = "stunting"
    PLANT_GROWTH_RETARDATION = "plant_growth_retardation"

    HONEYDEW_EXCRETION = "honeydew_excretion"
    SOOTY_MOLD_GROWTH = "sooty_mold_growth"

    BORING = "boring"
    BOLL_BORING = "boll_boring"
    BOLL_DEFORMATION = "boll_deformation"
    REDUCED_BOLL_SIZE = "reduced_boll_size"
    YOUNG_BOLL_SHEDDING = "young_boll_shedding"
    SEED_DESTRUCTION = "seed_destruction"
    LOCULE_DAMAGE = "locule_damage"

    SHOOT_DISTORTION = "shoot_distortion"
    STEM_DAMAGE = "stem_damage"
    ROOT_DAMAGE = "root_damage"

    PREMATURE_DEFOLIATION = "premature_defoliation"
    FLOWER_SHEDDING = "flower_shedding"
    SQUARE_SHEDDING = "square_shedding"


class FeedingBehavior(PestSenseEnum):
    NONE = "none"
    SAP_SUCKING = "sap_sucking"
    PHLOEM_SAP_SUCKING = "phloem_sap_sucking"
    RASPING_AND_SUCKING = "rasping_and_sucking"
    BOLL_BORING_SEED_DESTRUCTION = "boll_boring_seed_destruction"
    OVIPOSITION_ON_BOLLS = "oviposition_on_bolls"
    SAP_SUCKING_AND_VIRUS_TRANSMISSION = "sap_sucking_and_virus_transmission"


class MobilityLevel(PestSenseEnum):
    IMMOBILE = "immobile"
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ReproductionType(PestSenseEnum):
    SEXUAL = "sexual"
    SEXUAL_OVOVIVIPAROUS = "sexual_ovoviviparous"
    PARTHENOGENETIC = "parthenogenetic"
    PARTHENOGENETIC_LIVE_BIRTH = "parthenogenetic_live_birth"


class PressureProfile(PestSenseEnum):
    VERY_HIGH_IN_HOT_HUMID_IRRIGATED_PERIODS = "very_high_in_hot_humid_irrigated_periods"
    HIGH_DURING_VEGETATIVE_AND_EARLY_FLOWERING = "high_during_vegetative_and_early_flowering"
    MODERATE_HIGH_IN_HOT_DRY_EARLY_CROP_STAGE = "moderate_high_in_hot_dry_early_crop_stage"
    EPISODIC_OUTBREAKS_IN_MODERATE_CONDITIONS = "episodic_outbreaks_in_moderate_conditions"
    LOCALIZED_BUT_HIGH_WHEN_ESTABLISHED = "localized_but_high_when_established"
    HIGH_DURING_BOLL_FORMATION_AND_LATE_CROP = "high_during_boll_formation_and_late_crop"


class BiologicalEventType(PestSenseEnum):
    LIFECYCLE_TRANSITION = "lifecycle_transition"
    REPRODUCTIVE_WINDOW = "reproductive_window"
    RAPID_POPULATION_GROWTH = "rapid_population_growth"
    MIGRATION_RISK = "migration_risk"
    OVERLAPPING_GENERATIONS = "overlapping_generations"
    RESISTANCE_SUSPECTED = "resistance_suspected"