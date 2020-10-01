#SL Ultimate Control Settings
from consts import ON, OFF

SMART_VIEW = ON
INCLUDE_RETURN_TRACKS = ON
INVERT_MUTE_FEEDBACK = ON
SCENE_FOLLOWS_SESSION_BOX = OFF
TRACK_SELECT_ON_ARM = ON
P2_INVERT_SHIFT_MODE = ON
BROWSER_ENABLE = ON #require PAD_ROW_BASE to be defined in consts with custom CC number. 
# Those CC Number shall also be programmed accordingly on MK2 device in Ableton Template.

#BROWSER MODES IS CONTROLED USING PADS AND POTI ENCODERS
#PADS CONFIGURATION : 
# PADS shall be configured to send CC message instead of midi notes. 
# A .Syx preset is provided with valid Pad configuration and  is compliant with CC number 
# defined in consts.py. 
# The .Syx file only contains an alternative to default SL MK2 template for Ableton. 
# It will not overwrite others templates and global settings.
#
#BROWSER MODES :
# Different Browser Modes can be activated using LSHIFT + PADx
#           LSHIFT + PAD1 : activate CORE LIBRARY BROWSER Mode
#           LSHIFT + PAD2 : activate FAVORITES BROWSER Mode
#           LSHIFT + PAD3 : activate RECENTS BROWSER Mode
#           LSHIFT + PAD4 : activate HOTSWAP BROWER Mode -Allow to select and swap only 
#                           preset for the selected device category
#           LSHIFT + PAD5 : activate CUSTOM BROWSER Mode -customizable actions menu 
#                           and Pad Assignments 
#
#POTI ENCODERS are used for navigation, in all Browser modes  :
#       POT1 = BROWSE LEVEL1 menu (TAGS) 
#       POT2 = BROWSE LEVEL2 menu (DEVICES)
#       POT3 = BROWSE LEVEL3 menu (PRESETS OR FOLDERS)
#       POT4 = BROWSE LEVEL4 menu (PRESETS WHEN INSIDE FOLDERS)
#       POT5 = FINE/SLOW BROWSING MODE
#       POT6 = PAD MAPPINGS BANK SELECT
#       POT7 = NOT USED
#       POT8 = NOT USED
#
#2 PAD Buttons are used to trigger action :
#   PAD1 = MAIN ACTION (=LOAD SELECTED PRESET for any browser mode except custom 
#                        browser mode, =ENTER for custom browser mode)
#   PAD2 = ALTERNATE ACTION 
#           = ADD TO (/ REMOVE FROM) FAVORITES for RECENT (/ FAVORITES) mode. 
#          (It is also used to Learn User Pad Assigment in custom browser mode, see below)
#
#USER PAD ASSIGMENTS :
# 6 Others PADS (x6 banks) are ready to be assigned to actions available in custom 
# browser modes :
#      - Custom Browser mode can be easily extended (see SLGlobalMenus.py and 
#        SLLiveActions.py) and any action provided there can be mapped to one/several 
#        user pads.
#      - To map a pad, you have to activate custom browser mode and select (MAIN ACTION) 
#        the pad in 'Shortcuts/Learn/BankX' menu.
#      - Then ,locate the action you wan to map in the differents menus. Instead of
#        launching it by hiting the MAIN ACTION pad, hit the ALTERNATE ACTION pad in
#        order to map the action to the previous selected pad (& selected pad bank).
#      - PAD3,PAD4,PAD5,PAD6,PAD7 and PAD8 are ready to be customized
#
#      - remember also that :
#           LSHIFT + PAD3 : activate RECENTS BROWSER Mode
#           LSHIFT + PAD4 : activate HOTSWAP BROWER MODE ON/OFF
#             (Allow to select and swap only presets ompliant with the selected device 
#              category)
#           LSHIFT + PAD5 : activate CUSTOM BROWSER Mode
#
#
# Pad Mappings, Recent and Favorites presets are stored in dedicated xml files
#    (see X_X_FILE below) to be retrieved from one Live session to one other.
#

AUTO_REFRESH_FOLDER_PREFIX = '_'
FAVORITE_PRESETS_FILE = 'favorite_presets_file.xml'
RECENT_PRESETS_FILE = 'recent_presets_autosave_file.xml'
SETTINGS_FILE = 'mappings_file.xml'
BACKUP_SETTINGS_FILE = 'mappings_autosave_file.xml'

MIDI1_TRACK_COLOR = 13107200 #R(200)
AUDIO_TRACK_COLOR =      200 #B(200)

DEFAULT_ENCODER_MODE = 8 #0 - Track, 1 - Pan, 2-7 - Send A-F, 8 - Device
DEFAULT_POT_MODE = 9     #0 - Track, 1 - Pan, 2-7 - Send A-F, 8 - Device, 9 - Browser

TEMPO_TOP = 200.0
TEMPO_BOTTOM = 60.0
