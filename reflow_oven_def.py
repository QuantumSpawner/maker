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
SMART_ASSIST_PROMPT_LABEL = True

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
SMART_ASSIST_START_LISTEN_BUTTON = True
START_BUTTON = True

# sliders
SLIDERS = True

TEMP_SLIDER = True
PERIOD_SLIDER = True

# message handler ##############################################################
FAKE_I2C = False

SLAVE_ADDRESS = 0x27
TEMP_ADDRESS = 0x40
TIME_ADDRESS = 0x50
TEMP_SETTING_ADDRESS = 0x00
TIME_SETTING_ADDRESS = 0x10
START_COMMAND = 0x20
RESET_COMMAND = 0x30
profile_update = 0x60

# oven controller ##############################################################
ADC_ADDRESS = 0x48
RELAY_PIN = 17

PID_DELTA_TIME = 1
PID_KP = 10
PID_KI = 0
PID_KD = 0

# smart assist #################################################################
PRINT_EVEYTHING = False
REPLAY_AUDIO = False


# control ######################################################################
class ReflowOvenControl:
    start_event = threading.Event()
    reset_event = threading.Event()
    start_listen_event = threading.Event()
    finish_listen_event = threading.Event()
    temp = queue.Queue()
    time = queue.Queue()
    temp_setting = queue.Queue()
    time_setting = queue.Queue()
    smart_assist_prompt = queue.Queue()
    smart_assist_temp_setting = queue.Queue()
    smart_assist_time_setting = queue.Queue()
