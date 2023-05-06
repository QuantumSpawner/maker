import threading
import queue

# display ######################################################################
SHOW_GRID = False
FULL_SCREEN = True

# labels
LABELS = True

TIME_LABEL = True
MODE_LABEL = True
PROFILE_LABEL = True
TIME_PASSED_LABEL = True
TIME_REMAINING_LABEL = True
CURRENT_TEMP_LABEL = True
TOTAL_TIME_LABEL = True
STAGE_SCROLL_LABEL = True
TEMP_SETTING_LABEL = True
PERIOD_SETTING_LABEL = True

# progress bar
PROGRESS_BAR = True

# temperature chart
TEMP_CHART = True
TEMP_POINT = True
REAL_TEMP_POINT = True

# buttons
BUTTONS = True

SHUTDOWN_BUTTON = True
SETTINGS_BUTTON = True
WIFI_BUTTON = True
MODE_BUTTON = True
PROFILE_BUTTON = True
STAGE_SCROLL_LEFT_BUTTON = True
STAGE_SCROLL_RIGHT_BUTTON = True
START_BUTTON = True

# sliders
SLIDERS = True

TEMP_SLIDER = True
PERIOD_SLIDER = True

# message handler ##############################################################
FAKE_I2C = False

SLAVE_ADDRESS = 0x27
TEMP_ADDRESS = ord('N')
TIME_ADDRESS = ord('C')
TEMP_SETTING_ADDRESS = ord('T')
TIME_SETTING_ADDRESS = ord('t')
START_COMMAND = ord('B')
RESET_COMMAND = ord('E')


# control ######################################################################
class ReflowOvenControl:
    start_event = threading.Event()
    reset_event = threading.Event()
    start_audio_event = threading.Event()
    temp = queue.Queue()
    time = queue.Queue()
    temp_setting = queue.Queue()
    time_setting = queue.Queue()
