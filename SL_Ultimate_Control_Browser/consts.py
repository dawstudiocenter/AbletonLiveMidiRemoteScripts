MIDI_CHANNEL = 0

P1_UP = 88
P1_DOWN = 89

P2_UP = 90
P2_DOWN = 91

SCENE_UP_BUTTON = 80
SCENE_DOWN_BUTTON = 81
SCENE_LAUNCH_BUTTON = 82
SHOW_POT_VALUES_BUTTON = 83
SHIFT_BUTTON = 84

SELECT_BUTTON_BASE = 24
CLIP_LAUNCH_BUTTON_BASE = 32

ENCODER_ROW_BASE = 56

PAD_ROW_BASE = 64 # CC number for PADS row as required for BROWSER Mode, CC number  shall be accordingly defined for pads on SL MK2 device

ENCODER_FEEDBACK_BASE = 112
ENCODER_LED_MODE_BASE = 120

POT_ROW_BASE = 8

SLIDER_ROW_BASE = 16
SLIDER_MODE_BUTTON = 85

MUTE_BUTTON_BASE = 40
MUTE_MODE_BUTTON = 86

SOLO_BUTTON_BASE = 48
SOLO_MODE_BUTTON = 87

TS_LOCK = 79
TS_REWIND = 72
TS_FORWARD = 73
TS_STOP = 74
TS_PLAY = 75
TS_LOOP = 77
TS_RECORD = 76

BUTTON_HOLD_DELAY = 7
BUTTON_DOUBLE_PRESS_DELAY = 3

NUM_CHARS_PER_DISPLAY_LINE = 72
NUM_CHARS_PER_DISPLAY_STRIP = NUM_CHARS_PER_DISPLAY_LINE/8

DISPLAY_FAST_DELAY = 14
DISPLAY_LONG_DELAY = 24#20

NONAME_CLIP = 'unnamed'#'noname'
GROUP_CLIP = 'group'
NO_CLIP = ' '
NO_CLIP_STOP_BUTTON = '-'
NO_CLIP_REC_BUTTON = '*'

QUAINTIZATION_TO_BEAT = [0, #None
                        32, #8 Bars
                        16, #4 Bars
                        8, #2 Bars
                        4, #1 Bar
                        2, #1/2
                        1.333333333333333, #1/2T
                        1, #1/4
                        0.6666666666666667, #1/4T
                        0.5, #1/8
                        0.3333333333333333, #1/8T
                        0.25, #1/16
                        0.1666666666666667, #1/16T
                        0.125]#1/32 

PEAK_LEVEL_ALERT = 0.921 #0.0 - 1.0

def __create_row_range(cc_base):
    return range(cc_base, (cc_base + 8))

select_buttons_ccs = __create_row_range(SELECT_BUTTON_BASE)
clip_launch_buttons_ccs = __create_row_range(CLIP_LAUNCH_BUTTON_BASE)
encoder_row_ccs = __create_row_range(ENCODER_ROW_BASE)
encoder_feedback_ccs = __create_row_range(ENCODER_FEEDBACK_BASE)
encoder_led_mode_ccs = __create_row_range(ENCODER_LED_MODE_BASE)
pot_row_ccs = __create_row_range(POT_ROW_BASE)
pad_row_ccs = __create_row_range(PAD_ROW_BASE)

slider_row_ccs = __create_row_range(SLIDER_ROW_BASE)
mute_buttons_ccs = __create_row_range(MUTE_BUTTON_BASE)
solo_buttons_ccs = __create_row_range(SOLO_BUTTON_BASE)
ts_ccs = [TS_REWIND, TS_FORWARD, TS_STOP, TS_PLAY, TS_LOOP, TS_RECORD]

CC_STATUS = 176
CC_VAL_BUTTON_PRESSED = 1
CC_VAL_BUTTON_RELEASED = 0

ABLETON_PID = 4

WELCOME_SYSEX_MESSAGE = (240, 0, 32, 41, 3, 3, 18, 0, ABLETON_PID, 0, 1, 1, 247)
GOOD_BYE_SYSEX_MESSAGE = (240, 0, 32, 41, 3, 3, 18, 0, ABLETON_PID, 0, 1, 0, 247)
CLEAR_LEFT_DISPLAY = (240, 00, 32, 41, 3, 3, 18, 0, ABLETON_PID, 0, 2, 2, 3, 247)
CLEAR_RIGHT_DISPLAY = (240, 00, 32, 41, 3, 3, 18, 0, ABLETON_PID, 0, 2, 2, 4, 247)
SYSEX_HEADER = (240, 0, 32, 41, 3, 3, 18, 0, ABLETON_PID, 0, 2, 1)

ALL_LEDS_OFF_MESSAGE = ((CC_STATUS + MIDI_CHANNEL), 78, 0)

PAD_TRANSLATION = ((0, 2, 36, 0),
 (1, 2, 37, 0),
 (2, 2, 38, 0),
 (3, 2, 39, 0),
 (0, 3, 40, 0),
 (1, 3, 41, 0),
 (2, 3, 42, 0),
 (3, 3, 43, 0))

ON = True
OFF = False

enable_debug_output = True

def debug_print(*a):
    """ Special function for debug output """
    if enable_debug_output:
        print ' '.join(map(str, a))
        
instance = None
        
def log_message(*message):
        """ Writes the given message into Live's main log file """
        message = '(%s) %s' % ('SLUltimateControl', ' '.join(map(str, message)))
        console_message = 'LOG: ' + message
        if debug_print != None:
            debug_print(console_message)
        else:
            print console_message
        if instance != None :
            instance.log_message(message)