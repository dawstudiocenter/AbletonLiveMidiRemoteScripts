import Live
from _Framework.SessionComponent import SessionComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.SubjectSlot import subject_slot
from consts import NONAME_CLIP, GROUP_CLIP, NO_CLIP, NO_CLIP_STOP_BUTTON, NO_CLIP_REC_BUTTON
from config import P2_INVERT_SHIFT_MODE, SCENE_FOLLOWS_SESSION_BOX

INITIAL_SCROLLING_DELAY = 5
INTERVAL_SCROLLING_DELAY = 1

class SLScene(SceneComponent):
    def __init__(self, num_slots, tracks_to_use_callback, session):
        self._session = session
        SceneComponent.__init__(self, num_slots, tracks_to_use_callback)
        
    @subject_slot('value')
    def _launch_value(self, value):
        if self.is_enabled():
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_scene(self._scene)
            elif self._scene != None:
                if self._delete_button and self._delete_button.is_pressed() and value:
                    self._do_delete_scene(self._scene)
                else:
                    self._do_launch_scene(value)
            if value and self._scene:
                self._session.show_scene(True, True)
            
    def set_launch_button(self, button):
        if self._launch_button != button:
            self._launch_button = button
            self._launch_value.subject = button
            self.update()

    def _create_clip_slot(self):
        return SLClipSlot(self._session)    

class SLSession(SessionComponent):
    ' Subclass of channel strip component using select button for (un)folding tracks '

    _session_component_ends_initialisation = False
    #scene_component_type = SLScene
    
    def __init__(self, num_tracks, num_scenes):
        self.track_increment = num_tracks
        self._support_mkII = False
        self._master_mode = False
        self._tracks_and_listeners = []
        #SessionComponent.__init__(self, num_tracks, num_scenes)
        super(SLSession, self).__init__(num_tracks, num_scenes)
        self._selected_scene = SLScene(self._num_tracks, self.tracks_to_use, self)
        self._shift_button = None #R.Shift
        self._show_scene_button = None
        self._scene_up_button = None
        self._scene_down_button = None
        self._scroll_up_ticks_delay = -1
        self._scroll_down_ticks_delay = -1
        self.update_all_listeners()
        self._register_timer_callback(self._on_custom_timer)
        self._end_initialisation()
        
    def disconnect(self):
        self._unregister_timer_callback(self._on_custom_timer)
        
        for index in range(len(self._tracks_and_listeners)):
            track = self._tracks_and_listeners[index][0]
            listener = self._tracks_and_listeners[index][2]
            if ((track != None) and (track not in self.song().return_tracks) and (track != self.song().master_track) and track.playing_slot_index_has_listener(listener)):
                track.remove_playing_slot_index_listener(listener)        
        #SessionComponent.disconnect(self)
        super(SLSession, self).disconnect()
        
        self.set_shift_button = None
        if (self._show_scene_button != None):
            self._show_scene_button.remove_value_listener(self._show_scene_value)
            self._show_scene_button = None     
        if (self._scene_up_button != None):
            self._scene_up_button.remove_value_listener(self._bank_up_value) 
            self._scene_up_button = None
        if (self._scene_down_button != None):
            self._scene_down_button.remove_value_listener(self._bank_down_value)
            self._scene_down_button = None
        self.set_stop_track_clip_buttons(None)
        
    def refresh_state(self):
        pass
    
    def _is_scrolling(self):
        return (0 in (self._scroll_up_ticks_delay,
                      self._scroll_down_ticks_delay))
    
    def on_enabled_changed(self):
        self._scroll_up_ticks_delay = -1
        self._scroll_down_ticks_delay = -1
        self.update()
        self._do_show_highlight()
        
    def update_all_listeners(self):
        all_tracks = self.song().tracks#self.tracks_to_use()
        for track in all_tracks:
            if (track) and not track.is_foldable and (track not in self.song().return_tracks) and (track != self.song().master_track):
                if not track.fired_slot_index_has_listener(self._update_stop_group_clips_led):
                    track.add_fired_slot_index_listener(self._update_stop_group_clips_led)
                if not track.playing_slot_index_has_listener(self._update_stop_group_clips_led):
                    track.add_playing_slot_index_listener(self._update_stop_group_clips_led)

        
    def on_track_list_changed(self):
        #SessionComponent.on_track_list_changed(self)
        super(SLSession, self).on_track_list_changed()
        self.update_all_listeners()
        self.update()
        return None
        
    def set_shift_button(self, button):
        self._shift_button = button
        
    def set_scene_bank_buttons(self, up_button, down_button):
        assert ((up_button == None) or isinstance(up_button, ButtonElement))
        assert ((down_button == None) or isinstance(down_button, ButtonElement))
        do_update = False
        if (up_button is not self._scene_up_button):
            do_update = True
            if (self._scene_up_button != None):
                self._scene_up_button.remove_value_listener(self._bank_up_value)
            self._scene_up_button = up_button
            if (self._scene_up_button != None):
                self._scene_up_button.add_value_listener(self._bank_up_value)
                self._scene_up_button.reset()
        if (down_button is not self._scene_down_button):
            do_update = True
            if (self._scene_down_button != None):
                self._scene_down_button.remove_value_listener(self._bank_down_value)
            self._scene_down_button = down_button
            if (self._scene_down_button != None):
                self._scene_down_button.add_value_listener(self._bank_down_value)
                self._scene_down_button.reset()
        #if do_update:
            ##self._rebuild_callback()
            #self.update()

    def _bank_up_value(self, value): #DOWN
        assert (value in range(128))
        assert (self._scene_up_button != None)
        if self.is_enabled():
            button_is_momentary = self._scene_up_button.is_momentary()
            if button_is_momentary:
                if (value != 0):
                    self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
                    if (len(self.song().scenes) > (self._scene_offset + 1)):
                        self._scene_up_button.turn_on()
                else:
                    self._scroll_up_ticks_delay = -1
                    self._scene_up_button.turn_off()
            if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
                self.set_offsets(self._track_offset, (self._scene_offset + 1))
                self.show_scene(True, True)
            if SCENE_FOLLOWS_SESSION_BOX and self.song().view.selected_scene != self.song().scenes[self._scene_offset]:
                self.song().view.selected_scene = self.song().scenes[self._scene_offset]

    def _bank_down_value(self, value): #UP
        assert (value in range(128))
        assert (self._scene_down_button != None)
        if self.is_enabled():
            button_is_momentary = self._scene_down_button.is_momentary()
            if button_is_momentary:
                if (value != 0):
                    self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
                    if (self._scene_offset > 0):
                        self._scene_down_button.turn_on()
                else:
                    self._scroll_down_ticks_delay = -1
                    self._scene_down_button.turn_off()
            if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
                self.set_offsets(self._track_offset, max(0, self._scene_offset - 1))
                self.show_scene(True, True)
            if SCENE_FOLLOWS_SESSION_BOX and self.song().view.selected_scene != self.song().scenes[self._scene_offset]:
                self.song().view.selected_scene = self.song().scenes[self._scene_offset]
  
    def prepare_bank_right(self):
        self.set_offsets(self.track_offset() + self.track_increment, self.scene_offset())
        if self._mixer._display._hold_left != 0 or self._mixer._encoder_mode_index in (0,8,9):
            self._mixer.show_selected_tracks(True)
        else:
            self._mixer._display.set_block_left(False)
        self._mixer._display.set_block_right(False)        
        
    def _bank_right(self):
        #return self.set_offsets(self.track_offset() + self._track_banking_increment, self.scene_offset())
        return self.prepare_bank_right()

    def prepare_bank_left(self):
        self.set_offsets(max(self.track_offset() - self.track_increment, 0), self.scene_offset())
        if self._mixer._display._hold_left != 0 or self._mixer._encoder_mode_index in (0,8,9):
            self._mixer.show_selected_tracks(True)
        else:
            self._mixer._display.set_block_left(False)
        self._mixer._display.set_block_right(False)        
        
    def _bank_left(self):
        #return self.set_offsets(max(self.track_offset() - self._track_banking_increment, 0), self.scene_offset())
        return self.prepare_bank_left()
    
    def _can_bank_right(self):
        shift = self._shift_button.is_pressed() if self._shift_button else False
        #ret = False
        #tracks = self.tracks_to_use()
        #if tracks:
            #ret = (len(self.tracks_to_use()) > (self._get_minimal_track_offset() + 1))
        return (len(self.tracks_to_use())- ((7-int(self._master_mode))*(int(not P2_INVERT_SHIFT_MODE ^ shift))  ) > (self._get_minimal_track_offset() + 1))
    #return len(self.tracks_to_use()) > self._get_minimal_track_offset() + 1

    def set_show_scene_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._show_scene_button != button):
            if (self._show_scene_button != None):
                self._show_scene_button.remove_value_listener(self._show_scene_value)
                self._show_scene_button.reset()
            self._show_scene_button = button
            if (self._show_scene_button != None):
                self._show_scene_button.add_value_listener(self._show_scene_value)
                self._show_scene_button.reset()
        
    def _show_scene_value(self, value):
        assert (self._show_scene_button != None)
        assert (value in range (128))
        if ((value != 0) or (not self._show_scene_button.is_momentary())):
            self.show_scene()
            self._mixer._display.set_block_left(True)
            #self._show_scene_button.turn_on()
        if (value == 0):
            self._mixer._display.set_block_left(False, True)
            #self._show_scene_button.turn_off()
        
    def show_scene(self, show_scene_name=True, long_delay=False):
        if self.is_enabled():
            if self.song().view.selected_scene in self.song().scenes:
                tracks = self.tracks_to_use()
                #track_names = ''
                clip_names = ''

                scene_index = self._scene_offset
                
                for index in range(len(self._mixer._channel_strips)):
                    track_index = (self._mixer._track_offset + index)
                    track = None
                    clipname = NO_CLIP
                    if (len(tracks) > track_index):
                        track = tracks[track_index]
                        if track in self.song().visible_tracks:
                            slot = track.clip_slots[scene_index]
                            if slot.has_clip:
                                clipname = slot.clip.name 
                                if len(clipname.strip()) == 0:
                                    clipname = NONAME_CLIP    
                            elif track.is_foldable:
                                if slot.controls_other_clips:
                                    clipname = GROUP_CLIP
                                    #if track.fold_state:
                                        #pass#clipname += '<'
                                    #else:
                                        #clipname += ' '+chr(126)#'>'
                                elif slot.has_stop_button:
                                    clipname = NO_CLIP_STOP_BUTTON
                            elif slot.has_stop_button:
                                if track.can_be_armed and track.arm:
                                    clipname = NO_CLIP_REC_BUTTON
                                else:
                                    clipname = NO_CLIP_STOP_BUTTON

                    if index != 7:
                        clip_names += self._mixer._display._adjust_strip_string(clipname)
                    else:
                        if self._master_mode:
                            clipname = '         '
                        if show_scene_name:
                            scene_num = str(self._scene_offset+1)
                            clipname = self._mixer._display._adjust_strip_string(clipname, 9 - len(scene_num)) + scene_num
                        clip_names += clipname                        
                        
                self._mixer._display.show_message_left(self._mixer._selected_tracks_string, clip_names, long_delay)
                if self._support_mkII:
                    self._mixer._display.show_message_right(self._mixer._selected_tracks_string, clip_names)
    
    def set_stop_track_clip_buttons(self, buttons):
        assert ((buttons == None) or (isinstance(buttons, tuple) and (len(buttons) == self._num_tracks)))
        if (self._stop_track_clip_buttons != buttons):
            if (self._stop_track_clip_buttons != None):
                for button in self._stop_track_clip_buttons:
                    button.remove_value_listener(self._stop_track_value)
                    button.reset()
            self._stop_track_clip_buttons = buttons
            if (self._stop_track_clip_buttons != None):
                for button in self._stop_track_clip_buttons:
                    assert isinstance(button, ButtonElement)
                    button.add_value_listener(self._stop_track_value, identify_sender=True)
                    button.reset()
                    self._on_fired_slot_index_changed(list(buttons).index(button))
            #self._rebuild_callback()
            #self.update()
            self._update_stop_track_clip_buttons()
            
    def _stop_track_value(self, value, sender):
        assert (self._stop_track_clip_buttons != None)
        assert (list(self._stop_track_clip_buttons).count(sender) == 1)
        assert (value in range(128))
        if self.is_enabled():
            if ((value is not 0) or (not sender.is_momentary())):
                if not self._mixer._shift_pressed:
                    tracks = self.tracks_to_use()
                    track_index = (list(self._stop_track_clip_buttons).index(sender) + self.track_offset())
                    if (track_index in range(len(tracks))) and (tracks[track_index] in self.song().tracks):
                        if self._master_mode and list(self._stop_track_clip_buttons).index(sender) == self._num_tracks-1:
                            pass
                        else:
                            tracks[track_index].stop_all_clips()
                else:
                    self.song().stop_all_clips()
                        
    def update(self):
        if self._allow_updates:
            self._horizontal_banking.update()
            self._update_select_buttons()
            self._update_stop_track_clip_buttons()
            self._update_stop_all_clips_button()
        else:
            self._update_requests += 1
            
    def set_track_banking_increment(self, increment):
        #SessionComponent.set_track_banking_increment(self, increment)
        self.track_increment = increment
        self._horizontal_banking.update()
            
    def _reassign_tracks(self):
        for index in range(len(self._tracks_and_listeners)):
            track = self._tracks_and_listeners[index][0]
            fire_listener = self._tracks_and_listeners[index][1]
            playing_listener = self._tracks_and_listeners[index][2]
            if (track != None) and (track not in self.song().return_tracks) and (track != self.song().master_track):
                if track.fired_slot_index_has_listener(fire_listener):
                    track.remove_fired_slot_index_listener(fire_listener)
                if track.playing_slot_index_has_listener(playing_listener):
                    track.remove_playing_slot_index_listener(playing_listener)

        self._tracks_and_listeners = []
        tracks_to_use = self.tracks_to_use()
        for index in range(self._num_tracks):
            fire_listener = lambda index = index:self._on_fired_slot_index_changed(index)

            playing_listener = lambda index = index:self._on_playing_slot_index_changed(index)

            track = None
            if ((self._track_offset + index) < len(tracks_to_use)):
                track = tracks_to_use[(self._track_offset + index)]
            if self._master_mode and index == self._num_tracks-1:
                track = None
            if (track != None) and (track not in self.song().return_tracks) and (track != self.song().master_track):
                self._tracks_and_listeners.append((track,
                 fire_listener,
                 playing_listener))
                track.add_fired_slot_index_listener(fire_listener)
                track.add_playing_slot_index_listener(playing_listener)
            else:
                if (self._stop_track_clip_buttons != None):
                    self._stop_track_clip_buttons[index].turn_off()            
            self._update_stop_clips_led(index)
            
        self._horizontal_banking.update()
            
    def _on_fired_slot_index_changed(self, index):
        self._update_stop_clips_led(index)

    def _on_playing_slot_index_changed(self, index):
        self._update_stop_clips_led(index)                        

    def _update_stop_clips_led(self, index):
        if self.is_enabled() and (self._stop_track_clip_buttons != None) and self._mixer._control_second_row and self._mixer._support_mkII:
            if ((index in range(len(self._tracks_and_listeners))) and (self._tracks_and_listeners[index][0] in self.song().tracks)):
                track = self._tracks_and_listeners[index][0]
                
                subtracks_playing = False
                if track.is_foldable:
                    for slot in track.clip_slots:
                        if slot.is_playing: #slot.playing_status
                            subtracks_playing = True
                            break 
                if (track.fired_slot_index == -2 or track.playing_slot_index > -1) or subtracks_playing:
                    self._stop_track_clip_buttons[index].turn_on()
                else:
                    self._stop_track_clip_buttons[index].turn_off()
                    
                #if not track.is_foldable: #UPDATE GROUP TRACKS
                    #self._update_stop_group_clips_led()

    def _update_stop_group_clips_led(self):
        tracks_to_use = self.tracks_to_use()
        for index in range(self._num_tracks):
            track = None
            if ((self._track_offset + index) < len(tracks_to_use)):
                track = tracks_to_use[(self._track_offset + index)]
            if (track != None) and (track not in self.song().return_tracks) and (track != self.song().master_track) and track.is_foldable:
                self._update_stop_clips_led(index)
        
    def _create_scene(self): #added
        return SLScene(self._num_tracks, self.tracks_to_use, self)
        #return self.scene_component_type(num_slots=self._num_tracks, tracks_to_use_callback=self.tracks_to_use) 

    def _on_custom_timer(self):
        if self.is_enabled():
            scroll_delays = [self._scroll_up_ticks_delay,
                             self._scroll_down_ticks_delay]
            if (scroll_delays.count(-1) < 4):
                scenes_increment = 0
                if (self._scroll_down_ticks_delay > -1):
                    if self._is_scrolling():
                        scenes_increment -= 1
                        self._scroll_down_ticks_delay = INTERVAL_SCROLLING_DELAY
                    self._scroll_down_ticks_delay -= 1
                if (self._scroll_up_ticks_delay > -1):
                    if self._is_scrolling():
                        scenes_increment += 1
                        self._scroll_up_ticks_delay = INTERVAL_SCROLLING_DELAY
                    self._scroll_up_ticks_delay -= 1
                new_scene_offset = max(0, (self._scene_offset + scenes_increment))
                if (new_scene_offset != self._scene_offset):
                    self.set_offsets(self._track_offset, new_scene_offset)
        if self._is_scrolling():
            if SCENE_FOLLOWS_SESSION_BOX and self.song().view.selected_scene != self.song().scenes[self._scene_offset]:
                self.song().view.selected_scene = self.song().scenes[self._scene_offset]  
            if (self._scroll_down_ticks_delay > -1) or (self._scroll_up_ticks_delay > -1):  
                self.show_scene(True, True)
        
    def _do_show_highlight(self): #added
        if self._highlighting_callback != None: 
            include_returns = False
            return_tracks = self.song().return_tracks 
            if len(return_tracks) > 0: 
                include_returns = return_tracks[0] in self.tracks_to_use() 
            self._show_highlight and self._highlighting_callback(self._track_offset, self._scene_offset, self.width()-int(self._master_mode), self.height(), include_returns) 
            #else: 
                #self._highlighting_callback(-1, -1, -1, -1, include_returns)
        
class SLClipSlot(ClipSlotComponent):
    
    def __init__(self, session):
        self._session = session
        self._last_beat = -1
        ClipSlotComponent.__init__(self)
        self.song().add_current_song_time_listener(self._on_song_time_changed)
        self.song().add_is_playing_listener(self._on_playing_status_changed)
  
    def disconnect(self):
        self.song().remove_current_song_time_listener(self._on_song_time_changed) 
        self.song().remove_is_playing_listener(self._on_playing_status_changed) 
        self.set_launch_button(None)
        ClipSlotComponent.disconnect(self)
        
    def _launch_value(self, value):
        if self.is_enabled():
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_clip(self._clip_slot)
            elif self._clip_slot != None:
                if self._duplicate_button and self._duplicate_button.is_pressed():
                    if value:
                        self._do_duplicate_clip()
                elif self._delete_button and self._delete_button.is_pressed():
                    if value:
                        self._do_delete_clip()
                #elif self._session._shift_button and self._session._shift_button.is_pressed() and value and self.has_clip():
                    #self._clip_slot.clip.stop()
                else:
                    self._do_launch_clip(value)
                    self._session.show_scene(True, True)

                    
    def _on_playing_status_changed(self):
        if self.is_enabled():
            self._last_beat = -1
            self.update()
            
    def _on_song_time_changed(self):
        curr_song_beat = int(self.song().current_song_time % 2)
        if self._last_beat != curr_song_beat:
            self.update()
            self._last_beat = curr_song_beat
             
    def update(self):
        if self._session._support_mkII:
            self._has_fired_slot = False
            if (Live.Application.get_application().get_major_version() == 9 and Live.Application.get_application().get_minor_version() > 0) or Live.Application.get_application().get_major_version() == 10 :
                button = self._launch_button_value.subject
            else:
                button = self._launch_button_value_slot.subject
            if self._allow_updates:
                if (self.is_enabled() and (button != None)):
                    if (self._clip_slot != None):
                        curr_song_beat = int(self.song().current_song_time % 2)
                        if self.has_clip():
                            if curr_song_beat == 1 or not self._clip_slot.clip.is_playing or not self.song().is_playing:
                                button.turn_on()
                            else:
                                button.turn_off()
                        elif self._clip_slot.controls_other_clips:
                            if curr_song_beat == 1 or self._clip_slot.playing_status == 0 or self._clip_slot.is_triggered or not self.song().is_playing:
                                button.turn_on()
                            else:
                                button.turn_off() 
                        elif self._clip_slot.is_triggered:
                            button.turn_on()
                        else:
                            button.turn_off()
                    else:
                        button.turn_off() 
            else:
                self._update_requests += 1
        return None       