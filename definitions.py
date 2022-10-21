from enum import Enum


FILE_IDENTIFIER = 'resurfemg_paramfile'


class ProcessTypology(Enum):
    CUT = '0'
    BAND_PASS = '1'
    HIGH_PASS = '2'
    LOW_PASS = '3'
    ECG_REMOVAL = '4'
    ENVELOPE = '5'


class EcgRemovalMethods(Enum):
    ICA = '1'
    GATING = '2'
    NONE = '3'


class EnvelopeMethod(Enum):
    RMS = '1'
    FILTERING = '2'
    NONE = '3'


class GatingMethod(Enum):
    ZERO_FILL = '0'
    INTERPOLATE = '1'
    AVERAGE_PRIOR_SEGMENT = '2'
    RUNNING_AVERAGE_RMS = '3'
