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


default_bandpass_low = 3
default_bandpass_high = 450
default_first_cut_percentage = 3
default_first_cut_tolerance = 5
default_ecg_removal_value = EcgRemovalMethods.ICA
default_envelope_value = EnvelopeMethod.RMS

# IDs for graphical elements

# DATA UPLOAD PAGE
CONFIRM_CENTERED = 'confirm-centered'
CWD = 'cwd'
CWD_FILES = 'cwd-files'
EMG_FREQUENCY_DIV = 'emg-frequency-div'
EMG_OPEN_CENTERED = 'open-centered-emg'
EMG_SAMPLING_FREQUENCY = 'emg-sample-freq'
FILE_PATH_INPUT = 'file-path-input'
LISTED_FILES = 'listed_file'
MODAL_CENTERED = 'modal-centered'
PARENT_DIR = 'parent-dir'
PATH_BTN = 'path-button'
STORED_CWD = 'stored-cwd'
VENT_FREQUENCY_DIV = 'ventilator-frequency-div'
VENT_OPEN_CENTERED = 'open-centered-vent'
VENT_SAMPLING_FREQUENCY = 'ventilator-sample-freq'
