from enum import Enum


class CloudType(Enum):
    CIRRUS = "Ci"
    CIRROCUMULUS = "Cc"
    CIRROSTRATUS = "Cs"
    ALTOSTRATUS = "As"
    ALTOCUMULUS = "Ac"
    STRATUS = "St"
    STRATOCUMULUS = "Sc"
    NIMBOSTRATUS = "Ns"
    CUMULUS = "Cu"
    CUMULONIMBUS = "Cb"

class WarningType(Enum):
    STRONG_WIND = "W"
    HEAVY_RAIN = "R"
    COLD_WAVE = "C"
    DRY = "D"
    TSUNAMI = "O"
    EARTHQUAKE_TSUNAMI = "N"
    HIGH_SEAS = "V"
    TYPHOON = "T"
    HEAVY_SNOW = "S"
    YELLOW_DUST = "Y"
    HEAT_WAVE = "H"
    FOG = "F"

class WarningCommand(Enum):
    FORECASTED = "1"
    UPGRADED = "2"
    LIFTED_FORECASTED = "3"
    LIFTED_UPGRADED = "4"
    EXTENDED = "5"
    DOWNGRADED = "6"
    LIFTED_DOWNGRADED = "7"