from __future__ import with_statement

import Live

from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Generic.util import DeviceAppointer
from _Framework.DeviceComponent import select_and_appoint_device

from consts import *
from SLSession import SLSession
from SLMixer import SLMixer
from SLDevice import SLDevice
from SLDeviceControl import SLDeviceControl
from SLEncoder import SLEncoder
from SLShiftableSelector import SLShiftableSelector
from SLRightShiftSelector import SLRightShiftSelector
from SLEncoderModeSelector import SLEncoderModeSelector
from SLMasterModeSelector import SLMasterModeSelector
from SLButtonModeSelector import SLButtonModeSelector
from SLButtonModeSelector import SLSpecialButton
#from SLMuteModeSelector import SLMuteModeSelector
from SLPotModeSelector import SLPotModeSelector
#from SLSessionModeSelector import SLSessionModeSelector
from SLTransport import SLTransport
#from SLTransportModeSelector import SLTransportModeSelector
from SLDisplay import SLDisplay

class SLUltimateControl(ControlSurface):
    __doc__ = " SL Ultimate Control "
    _script_name = "SL Ultimate Control Script for Live 9.1.2"
    _script_ver = "1.07"

    def __init__(self, c_instance):
        
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self._support_mkII = False
            self._lock_enquiry_delay = 0
            self._suppress_session_highlight = True
            
            self._shift_button = None
            self._shift_mode = None
            self._right_shift = None
            self._encoder_modes = None
            self._pot_modes = None
            self._master_mode = None
            self._button_modes = None
            self._mute_mode = None
            self._transport_mode = None
            
            self._automap_has_control = False
            self.log(self._script_name+' '+self._script_ver)
            self.log('initialization')
            #self.set_suppress_rebuild_requests(True)
            self._device_selection_follows_track_selection = True
            self._scene_up_button = None
            self._scene_down_button = None
            self._scene_launch_button = None
            self._clip_launch_buttons = []
            self._ts_buttons = []
            
            self._encoders = None
            self._session = None
            self._mixer = None 
            self._transport = None
            self._device = None
            self._device_control = None
            self._display = SLDisplay(self)
            self._display.set_block_messages(True)
            self._setup_session_control()
            self._setup_mixer_control()
            self._session.set_mixer(self._mixer)
            self._shift_button.name = 'Shift_Button'
            self._setup_custom_controls() 
    
            self.song().master_track.add_output_meter_level_listener(self._on_master_peak_level_changed)
            
            self.set_pad_translations(PAD_TRANSLATION)
            #self.set_suppress_rebuild_requests(False)
            
            self._displays.append(self._display)
            
           
            #self._session._do_show_highlight()
            
            self._update_hardware_delay = -1
            
            self.set_highlighting_session_component(self._session)
            self._suppress_session_highlight = False
            
            #self._display.set_block_messages(False)
            
            self.show_message(self.__doc__ + "script loaded...")
            self.log('loaded')
        return None

    def _set_appointed_device(self, device):
        select_and_appoint_device(self.song(), device)

    def disconnect(self):
        self._shift_mode = None
        self._right_shift = None
        self._encoder_modes = None
        self._pot_modes = None
        self._master_mode = None
        self._button_modes = None
        self._mute_mode = None
        self._transport_mode = None
        self._scene_up_button = None
        self._scene_down_button = None    
        self._clip_launch_buttons = None
        self._shift_button = None
        self._session = None
        self._mixer = None   
        self._transport = None
        self._device = None
        self._display = None
        self._master_mode = False
        self.song().master_track.remove_output_meter_level_listener(self._on_master_peak_level_changed)
        ControlSurface.disconnect(self)
        self._send_midi(ALL_LEDS_OFF_MESSAGE)
        #self._send_midi(CLEAR_LEFT_DISPLAY)
        #self._send_midi(CLEAR_RIGHT_DISPLAY)
        self._send_midi(GOOD_BYE_SYSEX_MESSAGE) 
        self.log('disconnected')
        return None
    
    def log(self, message):
        self.log_message((' '+message+' ').center(50,'='))
        
    def send_welcome(self):
        self._send_midi(WELCOME_SYSEX_MESSAGE)

    #def refresh_state(self):
        #ControlSurface.refresh_state(self)   

    def update_controls(self):
        if self._display:
            self._display.refresh_state()        
        ControlSurface.refresh_state(self)
        for display in self._displays:
            display.set_block_messages(False)

        self._display.show_message_left(self._script_name.center(72), ("Version "+self._script_ver).center(72), True)
        self._display.show_message_right(self._script_name.center(72), ("Version "+self._script_ver).center(72), True)
        #self.schedule_message(5, self._refresh_displays)

    #def update_display(self):
        #ControlSurface.update_display(self)
        #self._display.update()
        
    def refresh_state(self):
        self._update_hardware_delay = 5
        self._lock_enquiry_delay = 5
        
    def _update_hardware(self):
        self.send_welcome()#self._send_midi(WELCOME_SYSEX_MESSAGE)
        for index in range(4):
            self._send_midi(((CC_STATUS + MIDI_CHANNEL), index + 72, CC_VAL_BUTTON_RELEASED))  
        self._send_midi(((CC_STATUS + MIDI_CHANNEL), index + 77, CC_VAL_BUTTON_RELEASED)) 
        #self.schedule_message(1, self.send_welcome)
        #for component in self.components:
            #component.refresh_state()
            
    def update_display(self):
        if (self._update_hardware_delay > 0):
            self._update_hardware_delay -= 1
            if (self._update_hardware_delay == 0):
                self._update_hardware()
                self._update_hardware_delay = -1
        if self._lock_enquiry_delay > 0:
            self._lock_enquiry_delay -= 1
            if self._lock_enquiry_delay == 0:
                self._send_midi((176, 103, 1))
        ControlSurface.update_display(self)
        self._display.update()
        
    #def receive_midi(self, midi_bytes):
        ##self.log(str(midi_bytes))
        #if midi_bytes[0] & 240 == CC_STATUS:
            #cc_no = midi_bytes[1]
            #cc_value = midi_bytes[2] 
            #if cc_no == 79:
                #self.log(" ========= TRANSPORT LOCK: "+str(cc_value != 0))
        #with self.component_guard():
            #self._do_receive_midi(midi_bytes)        
        
    def handle_sysex(self, midi_bytes):
        if (midi_bytes[0] == 240):
            if len(midi_bytes) == 13 and midi_bytes[1:4] == (0, 32, 41):
                if ((midi_bytes[8] == ABLETON_PID) and (midi_bytes[10] == 1)):
                    support_mkII = midi_bytes[6] * 100 + midi_bytes[7] >= 1800
                    #support_mkII = False
                    self._support_mkII = support_mkII
                    self._mixer._support_mkII = support_mkII
                    self._session._support_mkII = support_mkII
                    self._transport._support_mkII = support_mkII
                    for encoder in self._encoders:
                        encoder._support_mkII = support_mkII
                        
                    self.log(' support_mkII = ' + str(support_mkII))
                    if (midi_bytes[11] == 1):
                        #self._automap_has_control = False
                        self._send_midi(ALL_LEDS_OFF_MESSAGE)
                    self.update_controls()
                    self._send_midi((176, 103, 1))#self._lock_enquiry_delay = 1
                    #else:
                        #self._automap_has_control = True
                        
    def _setup_session_control(self):
        is_momentary = True
        self._shift_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SHIFT_BUTTON)
        self._session = SLSession(8, 1)
        self._session.name = 'Session'
        #self._session.set_track_bank_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, P2_UP), ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, P2_DOWN))
        self._scene_up_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SCENE_UP_BUTTON)
        self._scene_down_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SCENE_DOWN_BUTTON)
        self._scene_launch_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SCENE_LAUNCH_BUTTON)
        #for index in range(8):
        #    self._clip_launch_buttons.append(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, clip_launch_buttons_ccs[index]))

    def _setup_mixer_control(self):
        is_momentary = True
        self._mixer = SLMixer(8, self._display, self._session)
        self._mixer.name = 'Mixer'
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'

    def _setup_custom_controls(self):
        is_momentary = True
        select_buttons = []
        
        encoders = []
        for track in range(8):
            select_buttons.append(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, select_buttons_ccs[track]))
        show_pot_values_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SHOW_POT_VALUES_BUTTON)

        for index in range(8):
            encoder_led_mode_button = ButtonElement(not is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, encoder_led_mode_ccs[index])
            encoder_feedback = EncoderElement(MIDI_CC_TYPE, MIDI_CHANNEL, encoder_feedback_ccs[index], Live.MidiMap.MapMode.absolute)            
            ringed_encoder = SLEncoder(MIDI_CC_TYPE, MIDI_CHANNEL, encoder_row_ccs[index], Live.MidiMap.MapMode.relative_smooth_signed_bit)
            ringed_encoder.add_value_listener(self._mixer.encoder_moved)
            ringed_encoder.set_ring_mode_button(encoder_led_mode_button)
            ringed_encoder.set_led_ring_feedback(encoder_feedback)
            ringed_encoder.name = 'Device_Control_' + str(index)
            encoder_led_mode_button.name = ringed_encoder.name + '_Ring_Mode_Button' 
            encoders.append(ringed_encoder)
        self._encoders = encoders

        self._device = SLDevice(self._mixer, self._display)
        self._device.name = 'Device_Component'
        self._device.set_parameter_controls(tuple(encoders))
        self.set_device_component(self._device)
        self._mixer._device = self._device

        self._device_appointer = DeviceAppointer(song=self.song(), appointed_device_setter=self._set_appointed_device)

        p1_buttons = []
        p1_buttons.append(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, P1_UP))
        p1_buttons.append(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, P1_DOWN))  

        self._encoder_modes = SLEncoderModeSelector(self._mixer, self._device, tuple(encoders))
        self._encoder_modes.name = 'encoder_modes'  
        self._encoder_modes.set_controls_to_translate(tuple(encoders))


        #==== OLD MODES
        #mute_buttons = [ ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, mute_buttons_ccs[index]) for index in range(8) ]
        #mute_mode_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, MUTE_MODE_BUTTON)
        #self._mute_mode = SLMuteModeSelector(mute_mode_button, tuple(mute_buttons), self._mixer)
        #solo_buttons = [ ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, solo_buttons_ccs[index]) for index in range(8) ]
        #ts_buttons = [ ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, ts_ccs[index]) for index in range(6) ]
        #solo_mode_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SOLO_MODE_BUTTON)
        #ts_lock_button = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, TS_LOCK)
        #self._transport = SLTransport(self, self._display)
        #self._transport.name = 'Transport'        
        #self._transport_mode = SLTransportModeSelector(ts_lock_button, tuple(ts_buttons), solo_mode_button, solo_buttons, self._transport, self._mixer)
        #==== NEW MODES
        mx_first_buttons = [ ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, mute_buttons_ccs[index]) for index in range(8) ]
        mx_first_row_select = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, MUTE_MODE_BUTTON)
        mx_second_buttons = [ ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, solo_buttons_ccs[index]) for index in range(8) ]
        mx_second_row_select = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SOLO_MODE_BUTTON)
        
        for index in range(6):
            self._ts_buttons.append(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, ts_ccs[index]))
        ts_lock_button = SLSpecialButton(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, TS_LOCK)
        self._transport = SLTransport(self, self._display)
        self._transport.name = 'Transport'
        
        self._button_modes = SLButtonModeSelector(self._mixer, self._session, mx_first_buttons, mx_second_buttons, self._transport, ts_lock_button, self._ts_buttons)
        #self._button_modes.set_mode_buttons((mx_first_row_select, mx_second_row_select))
        #self._button_modes.set_mode_toggle(mx_first_row_select)

        #--- SLSessionModeSelector TEST ---------------------
        for index in range(8):
            self._clip_launch_buttons.append(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, clip_launch_buttons_ccs[index]))        
        #session_modes = SLSessionModeSelector(self._session, self._mixer, self._scene_launch_button, tuple(self._clip_launch_buttons))
        #session_modes.set_mode_toggle(self._clip_launch_buttons[7])
        #session_modes.set_enabled(0)
        pots = []
        for index in range(8):
            pot = SliderElement(MIDI_CC_TYPE, MIDI_CHANNEL, pot_row_ccs[index])
            pot.add_value_listener(self._mixer.pot_moved)
            pots.append(pot)
        self._pot_modes = SLPotModeSelector(self._mixer, tuple(pots))
        self._pot_modes.set_controls_to_translate(tuple(pots))
        self._pot_modes.name = 'pot_modes'
        self._mixer._pots = tuple(pots)
        #----------------------------------------------------
        self._device_control = SLDeviceControl(self._device, self._display)
        
        
        self._shift_mode = SLShiftableSelector(tuple(select_buttons), show_pot_values_button, tuple(p1_buttons), self._scene_up_button, self._scene_down_button, self._scene_launch_button, self._session, self._mixer, self._encoder_modes, self._device, self._device_control, tuple(self._clip_launch_buttons), self._pot_modes)
        self._shift_mode.name = 'Shift_Modes'
        self._shift_mode.set_mode_toggle(self._shift_button)
        
        sliders = []
        for track in range(8):
            slider = SliderElement(MIDI_CC_TYPE, MIDI_CHANNEL, slider_row_ccs[track])
            slider.add_value_listener(self._mixer.slider_moved)
            sliders.append(slider)
            sliders[-1].name = str(track) + '_Volume_Control'
            
        mx_slider_row_select = ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, SLIDER_MODE_BUTTON)
        self.master_mode = SLMasterModeSelector(self._mixer, self._session, tuple(sliders), self._button_modes, self._shift_mode, self._encoder_modes, self._pot_modes)
        self.master_mode.set_controls_to_translate(tuple(sliders))
        self.master_mode.name = 'Master_Mode'
        
        self._right_shift = SLRightShiftSelector(self._mixer, self._session, self._transport, self.master_mode, mx_slider_row_select, self._button_modes, mx_first_row_select)
        self._right_shift.name = 'Right_Shift_Mode'
        self._right_shift.set_mode_toggle(mx_second_row_select)
        self._transport.set_shift_button(mx_second_row_select)
        self._session.set_shift_button(mx_second_row_select)
        self._session.set_track_bank_buttons(ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, P2_UP), ButtonElement(is_momentary, MIDI_CC_TYPE, MIDI_CHANNEL, P2_DOWN))
        for index in range(8):
            strip = self._mixer.channel_strip(index)
            strip.set_shift_button(mx_second_row_select)

    def _on_master_peak_level_changed(self):
        if self._support_mkII:
            peak = self.song().master_track.output_meter_level
            #self._display.hold_right_display("%.3f" % peak)
            if peak > PEAK_LEVEL_ALERT:
                self._send_midi(((CC_STATUS + MIDI_CHANNEL), 77, CC_VAL_BUTTON_PRESSED)) 
            else:
                self._send_midi(((CC_STATUS + MIDI_CHANNEL), 77, CC_VAL_BUTTON_RELEASED)) 
            
