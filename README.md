AbletonLiveMidiRemoteScripts
============================
Compatibility with Live 9 (>9.1) and Live 10

MIDI Remote Scripts for Ableton Live and Novation Remote 25 SL MK2 Device
Include original SL Ultimate Control script from Roman Sharov (version 1.07)


Please find a mod version of Roman' SL Ultimate Control script. The original script features are described in the 'SL Ultimate Control' pdf file .

This version add these major features :
- Browsing the Ableton Live library directly from the SL MK2.
- Browsing a custom menu providing basic/featured actions in Ableton
- Ability to map Pads to such actions. Several Pad assignment Banks are available (6 bank x 6 pads).
- load/store XML configuration files : Recent/Favorites Presets, User Pad configuration settings

This version allow also to browse Samples/Clips directly from SL MK2 device.
Per default, Samples/Clips are virtually grouped according to their first letter : AudioClip-A,....AbletonClip-A...
A naming convention applied to Samples allow you to have a more convenient browsing experience :
[LOOP]_[DRUMS/BASS/GUITAR/MULTI/SYNTH/VOCAL]_[COLLECTIONNAME]_[XXXBpm]_(SAMPLE_NAME).wav
or
[SHOT]_[BASS/SYNTH/FX/KICK/PERCUSSION/SONG/VOCAL]_[COLLECTIONNAME]_(SAMPLE_NAME).wav

Ex. for a drum loop of 128bpm part of a 'Swedish Pop Vol1' compilation set.
=> LOOP_DRUMS_Swedish Pop Vol1_128Bpm_(3_B_Kick_128).wav
Try it to see the difference on SL MK2 device.
Instrument lists will be configurable in a future version.


Other minor features:
- original script behavior of track select buttons have been customized in order
to allow overdub session recording when double pressed
(and when track is already armed and a clipslot is playing in this track).


System Requirements:
It has been tested on Remote 25 SL MK2 only.


Software Requirements:
It has been tested on Ableton 9.1 / 64 bits and 32bits under Windows XP,Seven and mac OS X (10.9.X), but should be also compatible with Ableton 9.0.x versions.


Video Tutorials:
24/12/2013 - Setup & Basic usage https://youtu.be/ZC1rqmmT7fQ


Version History:
1.1.4 - LATEST - Ableton Live 9.1.6 compatibility
1.1.3 - Fix Hotswap mode
1.1.2 - Add Samples & Clips Management - Fix Recent/Favorites autosave
1.1.1 - User Pad Actions display
1.1 - PADs user mappings - extended custom menus - new browsing method
1.0.7 - recent/favorites - custom menus
1.0.6 - INITIAL - core library browser


Source Repository:
GitHub (HERE)


What's new:
New 1.1.4 Mod version available.

Release Log:
1.1.4:
- New Features :
* None
- Improvment :
* None
-Bug fixes :
* fix Ableton Live 9.1.6 compatibility issues

1.1.3:
- New Features :
* None
- Improvment :
* None
-Bug fixes :
* Hotswap Mode activation issues

1.1.2:
- New Features :
* Ableton Samples & Clip browsing
- Improvment :
* Browser Menu refresh when adding/deleting presets in Ableton Live (not documented yet, based on special folder handling, require to customize Ableton virtualfolders.cfg)
-Bug fixes :
* Only one Recent/Favorites Presets is retrieved from xml file at startup
* Issues with Recent/Favorites mgmt for Max4Live devices


What's next:
- New Features :
* None yet
- Improvment :
* Documentation for Ableton virtualfolders.cfg configuration required for menu refresh => Not planned
-Bug fixes :
* None Yet


Additional Tools:
SL MkII Template Editor from NovationMusic.com


Pre-Requisites:
Implemented as an additional Extra Device Mode, it is based on Pots and it requires additionally PADs to be enabled and used.
PADs shall be midi-assigned to CC messages in Ableton template on MK2 device and the CC number used defined in consts.py.
It includes a syx preset file that may help you with CC message assigments for pads.
Use SLKk2Editor from Novationmusic.com in order to send it to SL MK2 and overwrite the default template 32 for Ableton.

HowTos:
Extract from config.py:
#BROWSER MODES IS CONTROLED USING PADS AND POTI ENCODERS
#PADS CONFIGURATION :
# PADS shall be configured to send CC message instead of midi notes.
# A .Syx preset is provided with valid Pad configuration and is compliant with CC number
# defined in consts.py.
# The .Syx file only contains an alternative to default SL MK2 template for Ableton.
# It will not overwrite others templates and global settings.
#
#BROWSER MODES :
# Different Browser Modes can be activated using LSHIFT + PADx
# LSHIFT + PAD1 : activate CORE LIBRARY BROWSER Mode
# LSHIFT + PAD2 : activate FAVORITES BROWSER Mode
# LSHIFT + PAD3 : activate RECENTS BROWSER Mode
# LSHIFT + PAD4 : activate HOTSWAP BROWER Mode -Allow to select and swap only
# preset for the selected device category
# LSHIFT + PAD5 : activate CUSTOM BROWSER Mode -customizable actions menu
# and Pad Assignments
#
#POTI ENCODERS are used for navigation, in all Browser modes :
# POT1 = BROWSE LEVEL1 menu (TAGS)
# POT2 = BROWSE LEVEL2 menu (DEVICES)
# POT3 = BROWSE LEVEL3 menu (PRESETS OR FOLDERS)
# POT4 = BROWSE LEVEL4 menu (PRESETS WHEN INSIDE FOLDERS)
# POT5 = FINE/SLOW BROWSING MODE
# POT6 = PAD MAPPINGS BANK SELECT
# POT7 = NOT USED
# POT8 = NOT USED
#
#2 PAD Buttons are used to trigger action :
# PAD1 = MAIN ACTION (=LOAD SELECTED PRESET for any browser mode except custom
# browser mode, =ENTER for custom browser mode)
# PAD2 = ALTERNATE ACTION
# = ADD TO (/ REMOVE FROM) FAVORITES for RECENT (/ FAVORITES) mode.
# (It is also used to Learn User Pad Assigment in custom browser mode, see below)
#
#USER PAD ASSIGMENTS :
# 6 Others PADS (x6 banks) are ready to be assigned to actions available in custom
# browser modes :
# - Custom Browser mode can be easily extended (see SLGlobalMenus.py and
# SLLiveActions.py) and any action provided there can be mapped to one/several
# user pads.
# - To map a pad, you have to activate custom browser mode and select (MAIN ACTION)
# the pad in 'Shortcuts/Learn/BankX' menu.
# - Then ,locate the action you wan to map in the differents menus. Instead of
# launching it by hiting the MAIN ACTION pad, hit the ALTERNATE ACTION pad in
# order to map the action to the previous selected pad (& selected pad bank).
# - PAD3,PAD4,PAD5,PAD6,PAD7 and PAD8 are ready to be customized
#
# - remember also that :
# LSHIFT + PAD3 : activate RECENTS BROWSER Mode
# LSHIFT + PAD4 : activate HOTSWAP BROWER MODE ON/OFF
# (Allow to select and swap only presets ompliant with the selected device
# category)
# LSHIFT + PAD5 : activate CUSTOM BROWSER Mode
#
#
# Pad Mappings, Recent and Favorites presets are stored in dedicated xml files
# (see X_X_FILE below) to be retrieved from one Live session to one other.
# ...

FAQ:
Is it required to overwrite factory SL MK2 presets with your "Ableton Live" template ?
Overwrite the default Ableton template with the provided template is not a requirement, if you know
how to change pads midi mapping directly on your SL MK2 device. It's the only difference with default template.
PADs CC message number shall start with value 64 for 1st pad starting from left, then 65 for 2nd pad,
... and so on til the 8th pad.
How configure the Ableton midi section ?
Concerning Ableton MIDI configuration (track, sync, remote), both Ultimate Control Browser & Extra Device Browser shall be activated using SL MK2 PORT2 as input AND output.SL MK2 PORT2 input and output shall be configured to receive/send TRACK and REMOTE messages. NOT SYNC.
It’s the same for legacy Ultimate Control and Extra Device.
What are the differences between version tree for the SL Ultimate Control Browser and SL Ultimate Control scripts ?
Version tree are independent since both scripts have their own life cycle and are not maintained by the same person. Only Ableton version upgrade may require synchronized update.
The version displayed on LCD screen at startup (ex. “1.0.8”) is linked to legacy SL Ultimate Control script versions made and maintained by Roman Sharov.
The script SL Ultimate Control Browser is derived from this script and add additional features like Ableton browser access from the SL MK2. This script has its own downloadable (but not displayed) version tree (ex. 1.1.4).
Support:
PM me with your Ableton log file for support on script installation issues or usage bugs.
Ableton Log File in windows (7) :
\Users\[username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\Log.txt

First thing I would ask for further investigation is that you test your SL MK2
and Ableton installation with Roman Sharov's original SL Ultimate Control scripts.
So if you can test it yourself first, it's better.

But:
=> Limited support for Ableton configuration (only if time and knowledge allow it).
=> Limited support for Novation SL MK2 devices (only if time and knowledge allow it).

And don't forget:
=> I extend and maintain this script for my own usage. I'm not paid for that.

Credits:
Thanks to Roman for its work on SL Ultimate Control original script. It makes this mod's possible.
Thanks to Stray (NativeKontrol) since its ClyphX & Device Browser M4L device inspire me a lot.
