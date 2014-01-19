from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import *
from config import INVERT_MUTE_FEEDBACK

class SLButtonModeSelector(ModeSelectorComponent):
    __doc__ = ' gfdgdfg '
    def __init__(self, mixer, session, mx_first_buttons, mx_second_buttons, transport, ts_lock_button, ts_buttons):
        assert len(mx_first_buttons) == 8
        assert len(mx_second_buttons) == 8
        ModeSelectorComponent.__init__(self)
        self._master_mode = False
        self._mixer = mixer
        self._session = session

        self._mx_first_buttons = mx_first_buttons
        self._mx_second_buttons = mx_second_buttons
        
        self._transport = transport
        self._ts_lock_button = ts_lock_button
        #self._ts_locked = False
        #self._ts_lock_button.turn_off()
        self._ts_lock_button.add_value_listener(self._ts_lock_value)
        self._ts_buttons = ts_buttons
        self._transport.set_seek_buttons(self._ts_buttons[1], self._ts_buttons[0])
        self._transport.set_stop_button(self._ts_buttons[2], self._mx_second_buttons[2])
        self._transport.set_play_button(self._ts_buttons[3], self._mx_second_buttons[3])
        self._transport.set_loop_button(self._ts_buttons[4], self._mx_second_buttons[4]) 
        self._transport.set_record_button(self._ts_buttons[5], self._mx_second_buttons[5])          
        self.set_mode(0)

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._mixer = None
        self._mx_first_buttons = None
        self._mx_second_buttons = None
        self._transport = None
        self._ts_lock_button.remove_value_listener(self._ts_lock_value)
        self._ts_lock_button = None
        self._ts_buttons = None
        return None
        
    def number_of_modes(self):
        return 2

    def update(self):
        #for index in range(len(self._modes_buttons)):
            #if (index == self._mode_index):
                #self._modes_buttons[index].turn_on()
            #else:
                #self._modes_buttons[index].turn_off()
        self.update_first_row()
        self.update_second_row()
        self._transport._on_playing_status_changed()
        self._transport._on_loop_status_changed()
        self._transport._on_record_status_changed()
        for index in range(8):
            self._mixer.channel_strip(index)._on_solo_changed()
        self._session._update_stop_track_clip_buttons()
        return None
  
    def update_first_row(self):
        if not self._transport._ts_locked: #TS UNLOCKED
            if self._mixer._support_mkII:
                self._transport.set_nudge_buttons(None, None)
                self._transport.set_tap_tempo_button(None)
                self._transport.set_metronome_button(None)
                self._transport.set_quant_toggle_button(None)
                self._transport.set_session_record_button(None)
                self._transport.set_record_automation_button(None)
                self._transport.set_undo_button(None)

            if (self._mode_index == 0): #MUTE MODE
                for index in range(8):
                    self._mixer.channel_strip(index).set_arm_button(None)
                self._mixer.master_strip().set_arm_button(None)
                    
                for index in range(7):
                    self._mixer.channel_strip(index).set_mute_button(self._mx_first_buttons[index])
                    self._mixer.channel_strip(index).set_invert_mute_feedback(INVERT_MUTE_FEEDBACK)
                    
            elif (self._mode_index == 1): #ARM MODE
                for index in range(8):
                    self._mixer.channel_strip(index).set_mute_button(None)
                self._mixer.master_strip().set_mute_button(None)
                
                for index in range(7):
                    self._mixer.channel_strip(index).set_arm_button(self._mx_first_buttons[index])
                
                    
                    

        elif self._mixer._support_mkII: #TS LOCKED
            for index in range(8):
                self._mixer.channel_strip(index).set_mute_button(None)
                self._mixer.channel_strip(index).set_arm_button(None)
            self._mixer.master_strip().set_mute_button(None)
            self._mixer.master_strip().set_arm_button(None)
            
            self._transport.set_nudge_buttons(self._mx_first_buttons[1], self._mx_first_buttons[0])
            self._mx_first_buttons[2].turn_off()                
            self._transport.set_tap_tempo_button(self._mx_first_buttons[2])
            self._transport.set_metronome_button(self._mx_first_buttons[3])
            self._transport.set_quant_toggle_button(self._mx_first_buttons[4])
            self._transport.set_session_record_button(self._mx_first_buttons[5])
            self._transport.set_record_automation_button(self._mx_first_buttons[6])
            self._transport.set_undo_button(self._mx_first_buttons[7])

            self._transport._on_rec_quantisation_changed()            
            
        self.update_first_row_master_mode()
            
    def update_second_row(self):
        if not self._transport._ts_locked: #TS UNLOCKED
            if self._mixer._support_mkII:
                #self._ts_lock_button.turn_off()
                #self._transport.set_seek_buttons(None, None)
                self._transport.set_dummy1_button(None)
                self._transport.set_dummy2_button(None)
                self._transport.set_dummy7_button(None)
                self._transport.set_dummy8_button(None)
                #self._transport.set_stop_button(None, None)
                #self._transport.set_play_button(None, None)
                #self._transport.set_loop_button(None, None)  
                #self._transport.set_record_button(None, None)
            self._session.set_stop_track_clip_buttons(None)
            
            if (self._mode_index == 0): #SOLO MODE
                
                for index in range(7):
                    self._mixer.channel_strip(index).set_solo_button(self._mx_second_buttons[index])
                self.update_second_row_master_mode()
                    
            elif (self._mode_index == 1): #SPECIAL MODE
                for index in range(8):
                    self._mixer.channel_strip(index).set_solo_button(None)
                self._mixer.master_strip().set_solo_button(None)
                
                self._session.set_stop_track_clip_buttons(tuple(self._mx_second_buttons))
                
                        
        elif self._mixer._support_mkII: #TS LOCKED
            #self._ts_lock_button.turn_on()
            for index in range(8):
                self._mixer.channel_strip(index).set_solo_button(None)
            self._mixer.master_strip().set_solo_button(None)
            self._session.set_stop_track_clip_buttons(None)
            
            #self._transport.set_seek_buttons(self._ts_buttons[1], self._ts_buttons[0])
            #self._transport.set_stop_button(self._ts_buttons[2], self._mx_second_buttons[2])
            #self._transport.set_play_button(self._ts_buttons[3], self._mx_second_buttons[3])
            #self._transport.set_loop_button(self._ts_buttons[4], self._mx_second_buttons[4])  
            #self._transport.set_record_button(self._ts_buttons[5], self._mx_second_buttons[5])
            ##self._transport._on_record_status_changed()
            
            self._transport.set_dummy1_button(self._mx_second_buttons[0])
            self._transport.set_dummy2_button(self._mx_second_buttons[1])
            self._transport.set_dummy7_button(self._mx_second_buttons[6])
            self._mx_second_buttons[6].turn_off()
            self._transport.set_dummy8_button(self._mx_second_buttons[7])
            self._mx_second_buttons[7].turn_off()

    def update_master_mode(self):
        self.update_first_row_master_mode()
        self.update_second_row_master_mode()

    def update_first_row_master_mode(self):
        strip = self._mixer.channel_strip(7)
        master_strip = self._mixer.master_strip()
        button = self._mx_first_buttons[7]
        if not self._transport._ts_locked: #TS UNLOCKED
            if (self._mode_index == 0):
                if self._master_mode:
                    strip.set_mute_button(None)
                    master_strip.set_mute_button(button)
                else:
                    master_strip.set_mute_button(None)
                    strip.set_mute_button(button)
                    strip.set_invert_mute_feedback(INVERT_MUTE_FEEDBACK)                
            elif (self._mode_index == 1):
                if self._master_mode:
                    strip.set_arm_button(None)
                    master_strip.set_arm_button(button)
                else:
                    master_strip.set_arm_button(None)
                    strip.set_arm_button(button)
        
    def update_second_row_master_mode(self):
        strip = self._mixer.channel_strip(7)
        master_strip = self._mixer.master_strip()
        button = self._mx_second_buttons[7]
        if not self._transport._ts_locked: #TS UNLOCKED
            if (self._mode_index == 0): #SOLO MODE
                if self._master_mode:
                    strip.set_solo_button(None)
                    master_strip.set_solo_button(button)
                else:
                    master_strip.set_solo_button(None)
                    strip.set_solo_button(button)
            elif (self._mode_index == 1): #STOP TRACK MODE
                self._session._reassign_tracks()
                
    def set_mode(self, mode, force=False):
        assert isinstance(mode, int)
        assert (mode in range(self.number_of_modes()))
        if (self._mode_index != mode) or force:
            self._mode_index = mode
            self.update()
            
            
    def _ts_lock_value(self, value):
        assert (self._ts_lock_button != None)
        assert (value in range (128))
        self._transport._ts_locked = value == 1
        self._mixer._control_second_row = not self._transport._ts_locked
        self.update()
                
    def set_mode_toggle(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._mode_toggle != None):
            self._mode_toggle.remove_value_listener(self._toggle_value)
            self._mode_toggle.reset()
        self._mode_toggle = button
        if (self._mode_toggle != None):
            self._mode_toggle.add_value_listener(self._toggle_value)
            self.update_mode_toggle()
        return None
    
    def _toggle_value(self, value):
        assert (self._mode_toggle != None)
        assert isinstance(value, int)
        if ((value is not 0) or (not self._mode_toggle.is_momentary())):
            ts_was_locked = False
            if self._transport._ts_locked:
                self._transport._ts_locked = False
                self._mixer._control_second_row = not self._transport._ts_locked
                self._ts_lock_button.turn_off()
                ts_was_locked = True
            self.set_mode(((self._mode_index + 1) % self.number_of_modes()), ts_was_locked)
            self.show_modes()
        self.update_mode_toggle()
            
    def update_mode_toggle(self):
        if (self._mode_toggle != None):
            if (self._mode_index == 1):# and (self._toggle_pressed or self._mixer._shift_pressed):
                self._mode_toggle.turn_on()
            else:
                self._mode_toggle.turn_off()
        
    def show_modes(self, dublicate_on_left_display=False):
        top_str = ' First Button Row: '
        btm_str = 'Second Button Row: '
        if self._transport._ts_locked:
            top_str += '[SPECIAL]'
            btm_str += '[TRANSPORT]'
        elif (self._mode_index == 0):
            if INVERT_MUTE_FEEDBACK:
                top_str += '[TRACK ACTIVATE]'
            else:
                top_str += '[TRACK MUTE]'
            btm_str += '[TRACK SOLO/CUE]'
        elif (self._mode_index == 1):
            top_str += '[TRACK RECORD ARM]'
            btm_str += '[TRACK STOP]'
                
        #slider_str = ' Mixer: '
        #if not self._master_mode:
            #slider_str += '[8 CHANNELS]'
        #else:
            #slider_str += '[7 CHANNELS] + [MASTER]'
        #slider_str = slider_str.ljust(34)
        top_str = (' '*34 + top_str).ljust(72)#(slider_str + top_str).ljust(72)
        btm_str = (' '*34 + btm_str).ljust(72)
        
        self._mixer._display.show_message_right(top_str, btm_str)
        #if dublicate_on_left_display:
            #self._mixer._display.set_block_left(False)
            #self._mixer._display.show_message_left(top_str, btm_str)


class SLSpecialButton(ButtonElement):
    def __init__(self, is_momentary, msg_type, channel, identifier, undo_step_handler = DummyUndoStepHandler(), *a, **k):
        ButtonElement.__init__(self, is_momentary, msg_type, channel, identifier, undo_step_handler = DummyUndoStepHandler(), *a, **k)
        
    def disconnect(self):
        pass
    