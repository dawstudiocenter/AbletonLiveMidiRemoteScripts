import Live
from _Framework.TransportComponent import TransportComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework import Task

from consts import MIDI_CHANNEL, CC_STATUS, CC_VAL_BUTTON_PRESSED, CC_VAL_BUTTON_RELEASED, BUTTON_HOLD_DELAY, QUAINTIZATION_TO_BEAT

class SLTransport(TransportComponent):
    ' Subclass of channel strip component using select button for (un)folding tracks '

    def __init__(self, sl_surface, display):
        self._support_mkII = False
        self._ts_locked = False
        TransportComponent.__init__(self)
        self._sl = sl_surface
        self._shift_button = None
        self._shift_pressed = False
        self._display = display
        self._stop_button = None
        self._stop_button_pressed = False
        self._stop_button_pressed_time = 0
        self._stop_button_blink = False
        #self._stop_button_double_press = 0
        self._play_button = None
        self._loop_button = None
        self._record_button = None
        self._session_record_button = None
        self._record_automation_button = None
        
        self._nudge_up_button = None
        self._nudge_down_button = None
        
        self._main_view_button = None
        self._detail_view_button = None
        self._detail_view_button_pressed = False
        self._detail_view_button_pressed_time = 0
        
        self._metronome_button = None
        self._led_metronome = False
        self._last_beat = 5
        self._quant_toggle_button = None
        self._last_quant_value = Live.Song.RecordingQuantization.rec_q_eight
        self._clip_quant_values = QUAINTIZATION_TO_BEAT
        self._quant_names = ['Disabled', '1/4', '1/8', '1/8T', '1/8+T', '1/16', '1/16T', '1/16+T', '1/32']
        self._undo_button = None
        self._stop_button_feedback = None
        self._play_button_feedback = None
        self._loop_button_feedback = None  
        self._record_button_feedback = None
        self._dummy1_button = None
        self._dummy2_button = None
        self._dummy7_button = None
        self._dummy8_button = None
        self.song().add_is_playing_listener(self._on_playing_status_changed)
        self.song().add_record_mode_listener(self._on_record_status_changed)
        self.song().add_session_record_listener(self._on_session_record_status_changed)
        self.song().add_session_record_status_listener(self._on_session_record_status_changed)
        self.song().add_session_automation_record_listener(self._on_record_automation_changed)
        self.song().add_loop_listener(self._on_loop_status_changed)
        self.song().add_midi_recording_quantization_listener(self._on_rec_quantisation_changed)
        self.song().add_metronome_listener(self._on_metronome_changed)
        #self.song().add_clip_trigger_quantization_listener(self._on_clip_trigger_quantization_changed)
        self.song().add_current_song_time_listener(self._on_song_time_changed)
        self.song().add_nudge_down_listener(self._on_nudge_down_changed)
        self.song().add_nudge_up_listener(self._on_nudge_up_changed)        
        self._on_rec_quantisation_changed()
        self._update_undo_button_delay = 0
        self._register_timer_callback(self._on_custom_timer)
        return None        

    def disconnect(self):
        self._unregister_timer_callback(self._on_custom_timer)
        TransportComponent.disconnect(self)

        self.song().remove_is_playing_listener(self._on_playing_status_changed)
        self.song().remove_record_mode_listener(self._on_record_status_changed)
        self.song().remove_session_record_listener(self._on_session_record_status_changed)
        self.song().remove_session_record_status_listener(self._on_session_record_status_changed)
        self.song().remove_session_automation_record_listener(self._on_record_automation_changed)
        self.song().remove_loop_listener(self._on_loop_status_changed)
        self.song().remove_midi_recording_quantization_listener(self._on_rec_quantisation_changed)
        self.song().remove_metronome_listener(self._on_metronome_changed)
        self.song().remove_current_song_time_listener(self._on_song_time_changed)
        self.song().remove_nudge_down_listener(self._on_nudge_down_changed)
        self.song().remove_nudge_up_listener(self._on_nudge_up_changed)        
        
        self.set_shift_button(None)
        self.set_main_view_button(None)
        self.set_detail_view_button(None)
        self.set_undo_button(None)
        self.set_metronome_button(None)
        self.set_tap_tempo_button(None)
        self.set_quant_toggle_button(None)
        self.set_nudge_buttons(None, None)
        self.set_stop_button(None, None)
        self.set_play_button(None, None)
        self.set_loop_button(None, None)
        self.set_record_button(None, None)
        self.set_session_record_button(None)
        self.set_record_automation_button(None)
        self.set_dummy1_button(None)
        self.set_dummy2_button(None)
        self.set_dummy7_button(None)
        self.set_dummy8_button(None)

    def _on_timer(self):
        if not self._shift_pressed:
            if ((not self._ffwd_button_pressed) or (not self._rwd_button_pressed)):
                if self._ffwd_button_pressed:
                    self.song().current_song_time += 1
                elif self._rwd_button_pressed:
                    self.song().current_song_time = max(0, (self.song().current_song_time - 1))            

    def _on_custom_timer(self):
        if self.is_enabled():
            if self._stop_button_blink:
                if self._stop_button_feedback != None and not self.song().is_playing:
                    self._stop_button_feedback.turn_on()
                self._stop_button_blink = False
            self._update_undo_button_delay += 1
            if (self._update_undo_button_delay >= 20):
                self._update_undo_button_delay = 0
                self.update_undo_button()
            if self._stop_button_pressed:
                self._stop_button_pressed_time += 1
                if self._stop_button_pressed_time == BUTTON_HOLD_DELAY:
                    self._stop_button_feedback.turn_off()
                    self.song().stop_all_clips()
                    self._stop_button_blink = True                    
                    #if (self.song().back_to_arranger):
                        #self.song().back_to_arranger = False
                    #else:
                        #self.song().back_to_arranger = True
            #if (self._stop_button_double_press > 0):
                #self._stop_button_double_press -= 1               
            if self._detail_view_button_pressed:
                self._detail_view_button_pressed_time += 1
                if self._detail_view_button_pressed_time == BUTTON_HOLD_DELAY:
                    if self.application().view.is_view_visible('Detail'):
                        self.application().view.hide_view('Detail')                    
                
    def set_shift_button(self, button):
        assert ((button == None) or (isinstance(button, ButtonElement) and button.is_momentary()))
        if (button != self._shift_button):
            if (self._shift_button != None):
                self._shift_button.remove_value_listener(self._shift_value)
                self._shift_button.reset()
            self._shift_button = button
            if (self._shift_button != None):
                self._shift_button.add_value_listener(self._shift_value)
            
    def _shift_value(self, value):
        assert (self._shift_button != None)
        self._shift_pressed = (value != 0)
        self.update_undo_button()
        
    def set_undo_button(self, undo_button):
        assert ((undo_button == None) or isinstance(undo_button, ButtonElement))
        if self._undo_button != undo_button:
            if self._undo_button != None:
                self._undo_button.remove_value_listener(self._undo_value)
                self._undo_button.reset()
            self._undo_button = undo_button
            if self._undo_button != None:
                self._undo_button.add_value_listener(self._undo_value)
            self.update_undo_button()
        
    def _undo_value(self, value):
        assert (self._undo_button != None)
        assert (value in range (128))
        if ((value != 0) or (not self._undo_button.is_momentary())):
            if not self._shift_pressed:
                if self.song().can_undo:
                    self.song().undo()
            else:
                if self.song().can_redo:
                    self.song().redo()        
            self.update_undo_button()
            self.show_special_values()            
                
    def update_undo_button(self):
        if self._undo_button != None:
            if not self._shift_pressed:
                if self.song().can_undo:
                    self._undo_button.turn_on()
                else:
                    self._undo_button.turn_off()
            else:
                if self.song().can_redo:
                    self._undo_button.turn_on()
                else:
                    self._undo_button.turn_off()
                    
    def set_quant_toggle_button(self, button):
        assert ((button == None) or (isinstance(button, ButtonElement) and button.is_momentary()))
        if self._quant_toggle_button != button:
            if self._quant_toggle_button != None:
                self._quant_toggle_button.remove_value_listener(self._quant_toggle_value)
            self._quant_toggle_button = button
            if self._quant_toggle_button != None:
                self._quant_toggle_button.add_value_listener(self._quant_toggle_value)
            self._on_rec_quantisation_changed()   
            
    def set_metronome_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._metronome_button != button:
            if self._metronome_button != None:
                self._metronome_button.remove_value_listener(self._metronome_value)
            self._metronome_button = button
            if self._metronome_button != None:
                self._metronome_button.add_value_listener(self._metronome_value)
            self._on_metronome_changed()
        return None
    
    def set_tap_tempo_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._tap_tempo_button != button:
            if self._tap_tempo_button != None:
                self._tap_tempo_button.remove_value_listener(self._tap_tempo_value)
            self._tap_tempo_button = button
            if self._tap_tempo_button != None:
                self._tap_tempo_button.add_value_listener(self._tap_tempo_value)
            self.update()
        return None
    
    def set_dummy1_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._dummy1_button != button):
            if (self._dummy1_button != None):
                self._dummy1_button.remove_value_listener(self._dummy_value)
            self._dummy1_button = button
            if (self._dummy1_button != None):
                self._dummy1_button.add_value_listener(self._dummy_value)
   
            
    def set_dummy2_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._dummy2_button != button):
            if (self._dummy2_button != None):
                self._dummy2_button.remove_value_listener(self._dummy_value)
            self._dummy2_button = button
            if (self._dummy2_button != None):
                self._dummy2_button.add_value_listener(self._dummy_value)
            
    def set_dummy7_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._dummy7_button != button):
            if (self._dummy7_button != None):
                self._dummy7_button.remove_value_listener(self._dummy_value)
            self._dummy7_button = button
            if (self._dummy7_button != None):
                self._dummy7_button.add_value_listener(self._dummy_value)
            
    def set_dummy8_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._dummy8_button != button):
            if (self._dummy8_button != None):
                self._dummy8_button.remove_value_listener(self._dummy_value)
            self._dummy8_button = button
            if (self._dummy8_button != None):
                self._dummy8_button.add_value_listener(self._dummy_value)
        
    def _dummy_value(self, value):
        #assert (self._dummy1_button != None)
        assert isinstance(value, int)
        pass
            
    def set_nudge_buttons(self, up_button, down_button):
        assert ((up_button == None) or (isinstance(up_button, ButtonElement) and up_button.is_momentary()))
        assert ((down_button == None) or (isinstance(down_button, ButtonElement) and down_button.is_momentary()))
        if self._nudge_up_button != None:
            self._nudge_up_button.remove_value_listener(self._nudge_up_value)
        self._nudge_up_button = up_button
        if self._nudge_up_button != None:
            self._nudge_up_button.add_value_listener(self._nudge_up_value)
        if self._nudge_down_button != None:
            self._nudge_down_button.remove_value_listener(self._nudge_down_value)
        self._nudge_down_button = down_button
        if self._nudge_down_button != None:
            self._nudge_down_button.add_value_listener(self._nudge_down_value)
        #self.update()
        self._on_nudge_down_changed()
        self._on_nudge_up_changed()        
        return None
    
    def set_stop_button(self, button, button_feedback):
        assert ((button == None) or isinstance(button, ButtonElement))
        assert ((button_feedback == None) or isinstance(button_feedback, ButtonElement))
        if (self._stop_button != button):
            if (self._stop_button != None):
                self._stop_button.remove_value_listener(self._stop_value)
            self._stop_button = button
            if (self._stop_button != None):
                self._stop_button.add_value_listener(self._stop_value)
            if (self._stop_button_feedback != None):
                self._stop_button_feedback.remove_value_listener(self._dummy_value)
            self._stop_button_feedback = button_feedback
            if (self._stop_button_feedback != None):
                self._stop_button_feedback.add_value_listener(self._dummy_value)
            self._stop_button_pressed = False
            self._stop_button_pressed_time = 0                
            self._on_playing_status_changed()
            
    def set_play_button(self, button, button_feedback):
        assert ((button == None) or isinstance(button, ButtonElement))
        assert ((button_feedback == None) or isinstance(button_feedback, ButtonElement))
        if (self._play_button != button) or (self._play_button_feedback != button_feedback):
            if (self._play_button != None):
                self._play_button.remove_value_listener(self._play_value)
            self._play_button = button
            if (self._play_button != None):
                self._play_button.add_value_listener(self._play_value)
            if (self._play_button_feedback != None):
                self._play_button_feedback.remove_value_listener(self._dummy_value)
            self._play_button_feedback = button_feedback
            if (self._play_button_feedback != None):
                self._play_button_feedback.add_value_listener(self._dummy_value)            
            self._on_playing_status_changed()
            
    def set_loop_button(self, button, button_feedback):
        assert ((button == None) or isinstance(button, ButtonElement))
        assert ((button_feedback == None) or isinstance(button_feedback, ButtonElement))
        if self._loop_button != button:
            if self._loop_button != None:
                #self._loop_button.turn_off()
                self._loop_button.remove_value_listener(self._loop_value)
            self._loop_button = button
            if self._loop_button != None:
                self._loop_button.add_value_listener(self._loop_value)
            if self._loop_button_feedback != None:
                self._loop_button_feedback.remove_value_listener(self._dummy_value)
            self._loop_button_feedback = button_feedback
            if self._loop_button_feedback != None:
                self._loop_button_feedback.add_value_listener(self._dummy_value)
            self._on_loop_status_changed()
        return None    
    
    def set_record_button(self, button, button_feedback):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._record_button != button:
            if self._record_button != None:
                self._record_button.remove_value_listener(self._record_value)
            self._record_button = button
            if self._record_button != None:
                self._record_button.add_value_listener(self._record_value)
            if self._record_button_feedback != None:
                self._record_button_feedback.remove_value_listener(self._dummy_value)
            self._record_button_feedback = button_feedback
            if self._record_button_feedback != None:
                self._record_button_feedback.add_value_listener(self._dummy_value)            
            self._on_record_status_changed()
        return None
    
    def set_session_record_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._session_record_button != button:
            if self._session_record_button != None:
                self._session_record_button.remove_value_listener(self._session_record_value)
            self._session_record_button = button
            if self._session_record_button != None:
                self._session_record_button.add_value_listener(self._session_record_value)
            #self.update()
            self._on_session_record_status_changed()
        return None
    
    def set_record_automation_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._record_automation_button != button:
            if self._record_automation_button != None:
                self._record_automation_button.remove_value_listener(self._record_automation_value)
            self._record_automation_button = button
            if self._record_automation_button != None:
                self._record_automation_button.add_value_listener(self._record_automation_value)
            #self.update()
            self._on_record_automation_changed()
        return None
    
    def _quant_toggle_value(self, value):
        assert (self._quant_toggle_button != None)
        assert (value in range(128))
        assert (self._last_quant_value != Live.Song.RecordingQuantization.rec_q_no_q)
        if (self.is_enabled()):
            if ((value != 0) or (not self._quant_toggle_button.is_momentary())):
                if not self._shift_pressed:
                    quant_value = self.song().midi_recording_quantization
                    if (quant_value != Live.Song.RecordingQuantization.rec_q_no_q):
                        self._last_quant_value = quant_value
                        self.song().midi_recording_quantization = Live.Song.RecordingQuantization.rec_q_no_q
                    else:
                        self.song().midi_recording_quantization = self._last_quant_value  
                        
                    #clip = self.song().view.detail_clip
                    #if clip and clip.is_midi_clip:
                        #clip.quantize(Live.Song.RecordingQuantization.rec_q_thirtysecond, 0.15)
                    #self._sl.show_message("SWING "+str(self.song().swing_amount))
                else:
                    self._last_quant_value += 1
                    if self._last_quant_value == 9:
                        self._last_quant_value = 1
                    self.song().midi_recording_quantization = self._last_quant_value
                self.show_special_values()
                self._sl.show_message("MIDI Recording Quantization "+self._quant_names[self.song().midi_recording_quantization])
                
                
                
    def _move_current_song_time(self, speed, delta):
        song = self.song()
        song.current_song_time = max(0.0, song.current_song_time + speed * delta)
        ffd = 1
        if speed < 0:
            ffd = -1
        self.show_transport_values(ffd)  
        return Task.RUNNING

    def _rwd_value(self, value):
        if not self._shift_pressed:
            TransportComponent._rwd_value(self, value)
        elif self._rwd_button.is_momentary():
            self._rwd_task.kill()
            if value and self.song().can_jump_to_prev_cue:
                self.song().jump_to_prev_cue()             
        self.show_transport_values()
        
    def _ffwd_value(self, value):
        if not self._shift_pressed:
            TransportComponent._ffwd_value(self, value)
        elif self._ffwd_button.is_momentary():
            self._ffwd_task.kill()
            if value and self.song().can_jump_to_next_cue:
                self.song().jump_to_next_cue()                  
        self.show_transport_values()
    
    def _stop_value(self, value):
        assert (self._stop_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value != 0) or (not self._stop_button.is_momentary())):
                if not self._shift_pressed:
                    self.song().stop_playing()
                    self._on_playing_status_changed()
                    self._sl.schedule_message(2, self.show_transport_values)
                else:
                    #self.song().stop_all_clips()
                    if (self.song().back_to_arranger):
                        self.song().back_to_arranger = False
                    else:
                        self.song().back_to_arranger = True                    
                #if self._stop_button_double_press > 0:
                    #self.song().stop_all_clips()
                    #self._stop_button_double_press = 0
                #else:
                    #self._stop_button_double_press = DOUBLE_PRESS_DELAY                        
                self._stop_button_pressed = True
            else:
                self._stop_button_pressed = False
                self._stop_button_pressed_time = 0

    def _play_value(self, value):
        assert (self._play_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value != 0) or (not self._play_button.is_momentary())):
                if not self._shift_pressed:
                    self.song().start_playing()
                else:
                    self.song().continue_playing()
                self._sl.schedule_message(2, self.show_transport_values)
                                
    def _loop_value(self, value):
        assert (self._loop_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value != 0) or (not self._loop_button.is_momentary())):
                if not self._shift_pressed:
                    self.song().loop = (not self.song().loop)
                    self._sl.schedule_message(2, self.show_transport_values)
                else:
                    cue_points = self.song().cue_points
                    cue_points_num = len(cue_points)
                    if cue_points_num > 0:
                        current_time = self.song().current_song_time
                        loop_start = 0.0
                        loop_end = self.song().song_length#cue_points[cue_points_num-1].time
                        for index in range(cue_points_num):
                            cue_time = cue_points[index].time
                            if current_time >= cue_time and cue_time > loop_start:
                                loop_start = cue_time
                            if current_time < cue_time and cue_time < loop_end:
                                loop_end = cue_time
                        loop_length = 32.0
                        if loop_end > loop_start:
                            loop_length = loop_end - loop_start
                            #self._sl._display.show_message_right('song_length '+str(int(self.song().song_length))+ ' current_time '+str(int(current_time))+  '    loop_start '+str(int(loop_start))+ '   loop_end '+str(int(loop_end)))
                            try:
                                self.song().loop_start = loop_start
                            except RuntimeError:
                                pass
                            else:
                                self.song().loop_length = loop_length
                        
                
    def _record_value(self, value):
        assert (self._record_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value != 0) or (not self._record_button.is_momentary())):
                if not self._shift_pressed:
                    self.song().record_mode = (not self.song().record_mode)  
                else:
                    self.song().arrangement_overdub = (not self.song().arrangement_overdub)
                self._sl.schedule_message(2, self.show_transport_values)
                
    def _session_record_value(self, value):
        assert (self._session_record_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value != 0) or (not self._session_record_button.is_momentary())):
                if not self._shift_pressed:
                    if self.song().session_record_status != 1:
                        self.song().session_record = (not self.song().session_record)
                    else:
                        self.song().session_record = False
                else:
                    self.song().trigger_session_record()
                self.show_special_values()         
                #self._sl.schedule_message(2, self.show_transport_values)
                
    def _record_automation_value(self, value):
        assert (self._record_automation_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value != 0) or (not self._record_automation_button.is_momentary())):
                if not self._shift_pressed:
                    self.song().session_automation_record = (not self.song().session_automation_record)
                else:
                    self.song().re_enable_automation()
                #self.show_special_values()         
                self._sl.schedule_message(2, self.show_special_values)
                
    def _nudge_down_value(self, value):
        assert (self._nudge_down_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if (value != 0) or (not self._nudge_down_button.is_momentary()):
                if not self._shift_pressed:
                    self.song().nudge_down = True
                    self.show_special_values(-1)
                else:
                    if self.song().view.selected_track in self.song().tracks:
                        track_index = list(self.song().tracks).index(self.song().view.selected_track)
                        slot = self.song().view.selected_scene.clip_slots[track_index]
                        if ((slot != None) and slot.has_clip):
                            slot.clip.move_playing_pos(-self._clip_quant_values[self.song().clip_trigger_quantization])
                        self.show_special_values()                    
            else:
                self.song().nudge_down = False
                self.show_special_values()                 

    def _nudge_up_value(self, value):
        assert (self._nudge_up_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if (value != 0) or (not self._nudge_up_button.is_momentary()):
                if not self._shift_pressed:
                    self.song().nudge_up = (value != 0)
                    self.show_special_values(1)
                else:
                    if self.song().view.selected_track in self.song().tracks:
                        track_index = list(self.song().tracks).index(self.song().view.selected_track)
                        slot = self.song().view.selected_scene.clip_slots[track_index]
                        if ((slot != None) and slot.has_clip):
                            slot.clip.move_playing_pos(self._clip_quant_values[self.song().clip_trigger_quantization])
                        self.show_special_values()                                
            else:
                self.song().nudge_up = False
                self.show_special_values()                
            
    def _tap_tempo_value(self, value):
        assert (self._tap_tempo_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((value != 0) or (not self._tap_tempo_button.is_momentary())):
                self.song().tap_tempo() 
                self._tap_tempo_button.turn_on()
                #self.show_special_values()
                self._sl.schedule_message(2, self.show_special_values) 
            if (value == 0): 
                self._tap_tempo_button.turn_off()
                
    def _metronome_value(self, value):
        assert (self._metronome_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if ((value != 0) or (not self._metronome_button.is_momentary())):
                if not self._shift_pressed:
                    self.song().metronome = (not self.song().metronome)
                else:
                    self._led_metronome = not self._led_metronome
                    self._on_led_metronome_changed()                    
                self.show_special_values()
                
    def set_main_view_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._main_view_button != button:
            if self._main_view_button != None:
                self._main_view_button.remove_value_listener(self._main_view_value)
                self._main_view_button.reset()
            self._main_view_button = button
            if self._main_view_button != None:
                self._main_view_button.add_value_listener(self._main_view_value)

    def _main_view_value(self, value):
        assert (self._main_view_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if ((value != 0) or (not self._main_view_button.is_momentary())):
                if (not self.application().view.is_view_visible('Session')):
                    self.application().view.show_view('Session')
                else:
                    self.application().view.show_view('Arranger')

    def set_detail_view_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._detail_view_button != button:
            if self._detail_view_button != None:
                self._detail_view_button.remove_value_listener(self._detail_view_value)
                self._detail_view_button.reset()
            self._detail_view_button = button
            if self._detail_view_button != None:
                self._detail_view_button.add_value_listener(self._detail_view_value)
            self._detail_view_button_pressed = False
            self._detail_view_button_pressed_time = 0                    
        return None

    def _detail_view_value(self, value):
        assert (self._detail_view_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if ((value != 0) or (not self._detail_view_button.is_momentary())):
                if (not self.application().view.is_view_visible('Detail')):
                    self.application().view.show_view('Detail')
                else:
                    if (not self.application().view.is_view_visible('Detail/DeviceChain')):
                        self.application().view.show_view('Detail/DeviceChain')
                    else:
                        self.application().view.show_view('Detail/Clip')
                self._detail_view_button_pressed = True
            else:
                self._detail_view_button_pressed = False
                self._detail_view_button_pressed_time = 0
                    
    def update(self):
        TransportComponent.update(self)
        if self.is_enabled():
            self._on_playing_status_changed()
            self._on_record_status_changed()
            self._on_loop_status_changed()
            
            self._on_metronome_changed()
            self._on_session_record_status_changed()
    
            self._on_rec_quantisation_changed()
   
    def _on_rec_quantisation_changed(self):
        if self.is_enabled():
            quant_value = self.song().midi_recording_quantization
            quant_on = (quant_value != Live.Song.RecordingQuantization.rec_q_no_q)
            if quant_on:
                self._last_quant_value = quant_value
            if (self._quant_toggle_button != None):
                if quant_on:
                    self._quant_toggle_button.turn_on()
                else:
                    self._quant_toggle_button.turn_off()
                
    def _on_playing_status_changed(self):
        if self.is_enabled() and self._stop_button_feedback != None and self._play_button_feedback != None and self._ts_locked and self._support_mkII:
            if self.song().is_playing:
                self._stop_button_feedback.turn_off()
                self._play_button_feedback.turn_on()
            else:
                self._play_button_feedback.turn_off()
                self._stop_button_feedback.turn_on()   
  
    def _on_loop_status_changed(self):
        if self.is_enabled() and (self._loop_button_feedback != None) and self._ts_locked and self._support_mkII:
            if self.song().loop:
                self._loop_button_feedback.turn_on()
            else:
                self._loop_button_feedback.turn_off()    
        
    def _on_record_status_changed(self):
        if self.is_enabled() and self._record_button != None and self._record_button_feedback != None:
            if self.song().record_mode:
                self._record_button.turn_on()
            else:
                self._record_button.turn_off()
            if self._support_mkII and self._ts_locked:
                if self.song().record_mode:
                    self._record_button_feedback.turn_on()
                else:
                    self._record_button_feedback.turn_off()            
                    
    def _on_session_record_status_changed(self):
        if self.is_enabled():
            if (self._session_record_button != None):
                if self.song().session_record or self.song().session_record_status == 1:
                    self._session_record_button.turn_on()
                else:
                    self._session_record_button.turn_off()   
                    
    def _on_record_automation_changed(self):
        if self.is_enabled():
            if (self._record_automation_button != None):
                if self.song().session_automation_record:
                    self._record_automation_button.turn_on()
                else:
                    self._record_automation_button.turn_off()  
        
    def _on_metronome_changed(self):
        if self.is_enabled() and self._metronome_button != None:
            if self.song().metronome:
                self._metronome_button.turn_on()
            else:
                self._metronome_button.turn_off()
                
    def _on_led_metronome_changed(self):
        if self.is_enabled():
            if (self._metronome_button != None):
                if self._led_metronome:
                    song_time = str(self.song().get_current_beats_song_time()).split('.')
                    self.led_metronome_update(int(song_time[1]))
                else:
                    for index in range(4):
                        self._sl._send_midi(((CC_STATUS + MIDI_CHANNEL), index + 72, CC_VAL_BUTTON_RELEASED))   
                        
    def _on_song_time_changed(self):
        if self._led_metronome:
            song_time = str(self.song().get_current_beats_song_time()).split('.')
            beat = int(song_time[1])
            if beat != self._last_beat:
                self.led_metronome_update(beat)
                self._last_beat = beat

    def _on_nudge_down_changed(self):
        if self.is_enabled():
            if (self._nudge_down_button != None):
                if self.song().nudge_down:
                    self._nudge_down_button.turn_on()
                else:
                    self._nudge_down_button.turn_off()
                    
    def _on_nudge_up_changed(self):
        if self.is_enabled():
            if (self._nudge_up_button != None):
                if self.song().nudge_up:
                    self._nudge_up_button.turn_on()
                else:
                    self._nudge_up_button.turn_off()
                    
    def led_metronome_update(self, beat):
        for index in range(4):
            self._sl._send_midi(((CC_STATUS + MIDI_CHANNEL), index + 72, CC_VAL_BUTTON_RELEASED))
        self._sl._send_midi(((CC_STATUS + MIDI_CHANNEL), beat-1 + 72, CC_VAL_BUTTON_PRESSED))            
        return None
    
    def show_transport_values(self, ffwd=0):
        #top_str = ' Rewind  '+'Forward  '+'  Stop   '+'  Play   '+'  Loop   '+' Record  '
        top_str = ' Rewind  '+'Forward  '+'  Stop   '+'  Play   '+'  Loop   '+' Record '+chr(16)
        #if self.song().arrangement_overdub:
            #top_str += '|   Arrangement   ' 
        btm_str = ''
        if ffwd < 0:
            #btm_str += '  <<<    '
            btm_str += '  '+chr(127)*3+'    '
        else:
            btm_str += '         '
        if ffwd > 0:
            #btm_str += '  >>>    '
            btm_str += '  '+chr(126)*3+'    '
        else:
            btm_str += '         '   
        if self.song().is_playing:
            btm_str += '         '
        else:
            btm_str += ' STOPPED '
        if self.song().is_playing:
            #if not self.song().record_mode:
            btm_str += '   '+chr(126)*2+'    ' #' PLAYING '
            #else:
                #btm_str += 'RECORDING'
        else:
            btm_str += '         '            
        if self.song().loop:
            btm_str += '   ON    '
        else:
            btm_str += '         '  
        if self.song().record_mode:
            btm_str += '   ON   '
        else:
            btm_str += '        '
        if self.song().arrangement_overdub:
            #btm_str += '|     Overdub     '
            btm_str += '(Arrangmnt Overdub)'
        self._display.show_message_right(top_str, btm_str, True)
        if self._support_mkII:
            self._display.show_message_left(top_str, btm_str)
        
    def show_special_values(self, nudge=0):
        #top_str = ' Nudge-   Nudge+  TapTempo Metronome Automatn Session Quantiztn  Undo   '
        #         '        _        _        _        _        _        _        _        _'
        top_str = ' Nudge-   Nudge+  TapTempo Metronom Rec.Quant Session Automation  Undo '+chr(16)
        if self._shift_pressed:
            top_str = ' - Clip Nudge +   TapTempo Metronom Rec.Quant Session Automation  Redo '+chr(16)
        btm_str = ''
        if nudge < 0:
#           btm_str += '  <<<    '
            btm_str += '  '+chr(127)*3+'    '
        else:
            btm_str += '         '
        if nudge > 0:
            #btm_str += '  >>>    '
            btm_str += '  '+chr(126)*3+'    '
        else:
            btm_str += '         '        
        #btm_str += ("%.2f" % self.song().tempo).center(9)
        #btm_str += (str(int(self.song().tempo))+'  ').center(9)
        btm_str += (("%.2f" % self.song().tempo)+' ').center(9)
        if self.song().metronome:
            btm_str += '   ON    '
        else:
            btm_str += '         '
                
        if self.song().midi_recording_quantization != Live.Song.RecordingQuantization.rec_q_no_q:
            #btm_str += '   ON    '
            btm_str += self._quant_names[self.song().midi_recording_quantization].center(9)
        else:
            btm_str += '         '#'   OFF   '   
            
        if self.song().session_record or self.song().session_record_status == 1:
            btm_str += '   REC   '
        else:
            btm_str += '         ' 
            
        if self.song().session_automation_record:
            btm_str += '   ARM   '
        else:
            btm_str += '         '  

        #btm_str += '         '#'   OFF   '#+chr(16)        
        btm_str += '         '
        self._display.show_message_right(top_str, btm_str, True)
        if self._support_mkII:
            self._display.show_message_left(top_str, btm_str)
  
