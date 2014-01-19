import Live
from itertools import chain
from _Framework.MixerComponent import MixerComponent
from _Framework.ChannelStripComponent import ChannelStripComponent 
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
#from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.ControlSurface import ControlSurface

from consts import BUTTON_HOLD_DELAY, BUTTON_DOUBLE_PRESS_DELAY, DISPLAY_FAST_DELAY
from config import INCLUDE_RETURN_TRACKS, SMART_VIEW, TRACK_SELECT_ON_ARM, INVERT_MUTE_FEEDBACK, TEMPO_TOP, TEMPO_BOTTOM
from SLEncoder import SLEncoder

class SLMixer(MixerComponent):
    ' Special mixer class that uses return and master tracks alongside midi and audio tracks '

    def __init__(self, num_tracks, display, session):
        self._support_mkII = False
        self._control_second_row = True
        
        self._shift_pressed = False
        self._display = display
        self._session = session
        self._master_mode = False
        self._device = None
        self._extra_device = None

        self._rel_tempo_control = None
        self._rel_tempo_smooth_control = None
        self._rel_tempo_fine_control = None
        self._tempo_control_update_count = -1
        self._tempo_top = TEMPO_TOP
        self._tempo_bottom = TEMPO_BOTTOM
         
        #for right display
        self._track_names = [ '' for x in range(8) ]               #track1  track2  track3  track4  track5  track6  track7 
        self._track_volumes = [ None for x in range(8) ]             #0.0 dB  0.0 dB  0.0 dB  3.0 dB  0.0 dB -5.0 dB  0.0 dB  0.0 dB
        #for left display
        self._track_pans = [ None for x in range(8) ]                #  9L      C       C       32R     C       C       2L       C   
        self._track_sends = [ None for x in range(8) ]               #0.0 dB  0.0 dB  0.0 dB  0.0 dB  0.0 dB  0.0 dB  0.0 dB  0.0 dB

        self._mixer_names = ['Volume','Pan','Send A','Send B','Send C','Send D','Send E','Send F'] #['Send A','Send B','Send C','Send D','Send E','Send F','Pan','Volume']
        self._mixer_values = [ None for x in range(8) ]              #0.0 dB -1.0 dB  0.0 dB  2.0 dB                           32R
        
        self._selected_tracks_string = ''

        self._invert_mute_feedback = INVERT_MUTE_FEEDBACK
        self._encoder_mode_index = -1
        self._pot_mode_index = -1
        self._pots = None
        self._pot_moved = False
        self._show_pot_values_button = None
        
        MixerComponent.__init__(self, num_tracks)

        self.update_all_listeners()
        self._register_timer_callback(self._on_custom_timer)

    def disconnect(self):
        self._unregister_timer_callback(self._on_custom_timer)
        MixerComponent.disconnect(self)
        if (self._show_pot_values_button != None):
            self._show_pot_values_button.remove_value_listener(self._show_pot_values_value)
            self._show_pot_values_button = None        
        self.set_rel_tempo_control(None, None, None)
        
        self._display = None
        self._session = None
        self._device = None
        self._extra_device = None 
        
        self._track_names = None
        self._track_volumes = None
        self._track_pans = None
        self._track_sends = None

        self._mixer_names = None
        self._mixer_values = None
        
        self._pots = None

    def tracks_to_use(self):
        tracks = tuple(self.song().visible_tracks)
        if INCLUDE_RETURN_TRACKS:
            tracks += tuple(self.song().return_tracks)
        return tracks

    def _create_strip(self):
        return SLMixerStrip(self, self._session)

    def _reassign_tracks(self):
        MixerComponent._reassign_tracks(self)
        self.update_track_names()
        self.set_slider_values()        
        self.set_encoder_values()        

    def on_track_list_changed(self):
        if not self._offset_can_start_after_tracks:
            self._track_offset = min(self._track_offset, len(self.tracks_to_use()) - 1)
        self.update_all_listeners()
        self._reassign_tracks()
        self.show_selected_tracks(True)
        
    def update_selected_tracks_string(self):
        tracks = self.tracks_to_use()
        track_string = ''
        selected_track = self.song().view.selected_track
        for index in range(len(self._channel_strips)):
            track_index = (self._track_offset + index)
            track = None
            if (len(tracks) > track_index):
                track = tracks[track_index]

            if index == 7 and self._master_mode:
                if self.master_strip()._track == selected_track:
                    track_string = track_string[:-1] + '['                        
                    track_string += ' Master ]'
                else:
                    track_string += ' Master '+chr(16)
            else:
                track_name = self._track_names[index]
                
                #if track and track.is_foldable:
                    #track_name = self._display._adjust_strip_string(track_name,8)
                    #if track.fold_state:
                        #track_name = track_name[:-1]+'* '
                    #else:
                        #track_name = track_name[:-1]+chr(126)+' '                
                
                if track == selected_track:
                    if index != 0:
                        track_string = track_string[:-1] + '['
                    track_string += track_name[:-1]+']'
                else:
                    track_string += track_name[:-1]+chr(16)
        self._selected_tracks_string = track_string

    def update_all_listeners(self):
        pass
        all_tracks = self.tracks_to_use()
        for track in all_tracks:
            if (track):
                pass
                #if not track.mute_has_listener(self._on_track_mute_changed):
                    #track.add_mute_listener(self._on_track_mute_changed)
                #if not track.solo_has_listener(self._on_track_solo_changed):
                    #track.add_solo_listener(self._on_track_solo_changed)                    
                #if track.can_be_armed and not track.arm_has_listener(self._on_track_arm_changed):
                    #track.add_arm_listener(self._on_track_arm_changed)                    

                if not track.name_has_listener(self._on_track_name_changed):
                    track.add_name_listener(self._on_track_name_changed)
                if not track.mixer_device.volume.value_has_listener(self._on_track_volume_changed):
                    track.mixer_device.volume.add_value_listener(self._on_track_volume_changed)  
                #if not track.mixer_device.panning.value_has_listener(self._on_track_pan_or_sends_changed):
                    #track.mixer_device.panning.add_value_listener(self._on_track_pan_or_sends_changed)
        master_track = self.song().master_track
        if not master_track.mixer_device.volume.value_has_listener(self._on_track_volume_changed):
            master_track.mixer_device.volume.add_value_listener(self._on_track_volume_changed)        

    def _on_track_name_changed(self):
        #self._reassign_tracks()
        self.update_track_names()
        self.set_slider_values()
        self.set_encoder_values()

    def _on_track_volume_changed(self):
        self.set_slider_values()

    def _on_track_pan_or_sends_changed(self):
        #self.set_encoder_values()
        pass

    def update_track_names(self):
        for index in range(7):
            track = self.channel_strip(index)._track 
            if (track):
                if track.is_foldable:
                    track_name = self._display._adjust_strip_string(track.name,8)
                    if track.fold_state:
                        self._track_names[index] = track_name[:-1]+'* '
                    else:
                        self._track_names[index] = track_name[:-1]+chr(126)+' '
                else:
                    self._track_names[index] = self._display._adjust_strip_string(track.name)
            else:
                self._track_names[index] = ' '*9#self._display._adjust_strip_string('')
                
        if self._master_mode:
            self._track_names[7] = self._display._adjust_strip_string(self.master_strip()._track.name)
        else:
            track = self.channel_strip(7)._track 
            if (track):
                self._track_names[7] = self._display._adjust_strip_string(track.name)
            else:
                self._track_names[7] = ' '*9
        self.update_selected_tracks_string()
            
    def show_mute_values(self):
        if self._channel_strips:
            track_names = ''
            track_mutes = ''
            for index in range(7+int(not self._master_mode)):
                track = self.channel_strip(index)._track 
                track_name = ''
                track_mute = '       '+chr(16)
                if (track):
                    if track.mute and not self._invert_mute_feedback:
                        track_mute= chr(16)+' MUTED '+chr(16)
                    elif not track.mute and self._invert_mute_feedback:
                        track_mute = chr(16)+'ACTIVE'+chr(16)
                track_names += self._track_names[index]
                track_mutes += self._display._adjust_strip_string(track_mute)
                
            if self._master_mode:
                track_names += self._track_names[7]
                track_mutes += '       '+chr(16)

            self._display.show_message_right(track_names, track_mutes)
            if self._support_mkII:
                self._display.show_message_left(track_names, track_mutes)

    def show_arm_values(self, on_left_display=False):
        if self._channel_strips:
            track_names = ''
            track_arms = ''
            for index in range(7+int(not self._master_mode)):
                track = self.channel_strip(index)._track 
                track_name = ''
                track_arm = '       '+chr(16)
                if (track):
                    if track.can_be_armed and track.arm:
                        track_arm = '  ARMED '+chr(16)
                track_names += self._track_names[index]
                track_arms += self._display._adjust_strip_string(track_arm)

            if self._master_mode:
                track_names += self._track_names[7]
                track_arms += '       '+chr(16)

            if not on_left_display:
                self._display.show_message_right(track_names, track_arms)
            else:
                self._display.show_message_left(self._selected_tracks_string, track_arms)
        #if self._channel_strips:
            #track_names = ''
            #track_arms = ''
            #for index in range(7+int(not self._master_mode)):
                #track = self.channel_strip(index)._track 
                #track_name = ''
                #track_arm = '       '+chr(16)
                #if (track):
                    #if track.can_be_armed and track.arm:
                        #track_arm= '  ARMED '+chr(16)
                #track_names += self._track_names[index]
                #track_arms += self._display._adjust_strip_string(track_arm)

            #if self._master_mode:
                #track_names += self._track_names[7]
                #track_arms += '       '+chr(16)

            #if not on_left_display:
                #self._display.show_message_right(track_names, track_arms)
            #else:
                #self._display.show_message_left(track_names, track_arms)

    def show_solo_values(self):
        if self._channel_strips:
            track_names = ''
            track_solos = ''
            for index in range(7+int(not self._master_mode)):
                track = self.channel_strip(index)._track 
                track_name = ''
                track_solo = '       '+chr(16)
                if (track):
                    if track.solo:
                        track_solo= '  SOLO '+chr(16)
                        #track_solo= 'SOLO/CUE'+chr(16)
                track_names += self._track_names[index]
                track_solos += self._display._adjust_strip_string(track_solo)

            if self._master_mode:
                track_names += self._track_names[7]
                track_solos += '       '+chr(16)

            self._display.show_message_right(track_names, track_solos)
            if self._support_mkII:
                self._display.show_message_left(track_names, track_solos)

    def show_selected_tracks(self, long_delay=False):
        if self.is_enabled():
            #self._display.show_message_left(self._selected_tracks_string, ' Selected Track: ' + self.song().view.selected_track.name, long_delay)
            sel_track = ' Selected Track: ' + self.song().view.selected_track.name
            self._display.show_message_left(sel_track, self._selected_tracks_string, long_delay)
            #self._display.show_message_right(sel_track, self._selected_tracks_string)
            
            #tracks = self.tracks_to_use()
            #track_names = ''
            #selected_track = self.song().view.selected_track
            #for index in range(len(self._channel_strips)):
                #track_index = (self._track_offset + index)
                #track = None
                #if (len(tracks) > track_index):
                    #track = tracks[track_index]

                #if index == 7 and self._master_mode:
                    #if self.master_strip()._track == selected_track:
                        #track_names = track_names[:-1] + '['                        
                        #track_names += ' Master ]'
                    #else:
                        #track_names += ' Master '+chr(16)
                #else:
                    #if track == selected_track:
                        #if index != 0:
                            #track_names = track_names[:-1] + '['
                        #track_names += self._track_names[index][:-1]+']'
                    #else:
                        #track_names += self._track_names[index][:-1]+chr(16)

            #self._display.show_message_left(' Track: '+selected_track.name, track_names, long_delay)
                
            ##device_names = ''
            ##devices = selected_track.devices
            ##if devices:
                ##device_count = len(devices)
                ##for device in devices:
                    ##device_names += self._display._adjust_strip_string(device.name)
            ##self._display.show_message_left(device_names)
            
            ##if devices:
                ##device_count = len(devices)
                ###self._device.set_device(devices[device_count-1])
                ##self.song().view.select_device(devices[device_count-1])
                
    def set_slider_values(self):
        if self._channel_strips:
            for index in range(7):
                track = self.channel_strip(index)._track 
                if (track):
                    self._track_volumes[index] = track.mixer_device.volume#self.param_to_scale(track.mixer_device.volume)
                else:
                    self._track_volumes[index] = ''
            
            if self._master_mode:
                self._track_volumes[7] = self.master_strip()._track.mixer_device.volume#self.param_to_scale(self.master_strip()._track.mixer_device.volume)
            else:
                track = self.channel_strip(7)._track 
                if (track):
                    self._track_volumes[7] = track.mixer_device.volume#self.param_to_scale(track.mixer_device.volume)
                else:
                    self._track_volumes[7] = ''
            
            self._display.setup_right_display(self._track_names, self._track_volumes)
            
    #def param_to_scale(self, param):
        #str_value = ''
        #if param.value != param.min:
            #step = (param.max - param.min)/8
            #value = int(((param.value+(step/2))-param.min)/step)
            ##str_value = value*'='#chr(2) chr(126)
            #semivalue = int((param.value-param.min)/step)
            #str_value = semivalue*'='#chr(2) chr(126)
            #if semivalue != value:
                #str_value += '-'
            ##self._display.show_message_right(' value = '+str(value)+' semi = '+str(semivalue))
        #return str_value.ljust(8,chr(16))+' '#[:8]
        
    ##def param_to_scale(self, param):
        ##str_value = ''
        ##if param.value != param.min:
            ##step = (param.max - param.min)/8
            ##value = ((param.value+(step/2))-param.min)/step
            ##str_value = (int(value)*'*')#chr(2) chr(126)
        ##return str_value.ljust(8,'-')

    def encoder_moved(self, value):
        self._display.set_block_left(False)
    def slider_moved(self, value):
        #self._display.set_block_right(False)  
        self._display._hold_right = 0
        
    
    def set_show_pot_values_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._show_pot_values_button != button):
            if (self._show_pot_values_button != None):
                self._show_pot_values_button.remove_value_listener(self._show_pot_values_value)
                self._show_pot_values_button.reset()                
            self._show_pot_values_button = button
            self._display._pot_light_button = button
            self._display._hold_pot_light = -1
            if (self._show_pot_values_button != None):
                self._show_pot_values_button.add_value_listener(self._show_pot_values_value)
                self._show_pot_values_button.reset()

    def _show_pot_values_value(self, value):
        assert (self._show_pot_values_button != None)
        assert (value in range (128))
        if ((value != 0) or (not self._show_pot_values_button.is_momentary())):
            self.show_pot_values()
            self._display.set_block_left(True)
        else:
            self._display.set_block_left(False, True)
        
    def pot_moved(self, value):
        self._pot_moved = True

    def show_pot_values(self):
       
        if self._pot_mode_index == 8: # EXTRA DEVICE MODE
            #if self._extra_device != None:
            self._extra_device.show_device_values(True)
            #if not self._extra_device._locked_to_device:
                #if not self.application().view.is_view_visible('Detail'):
                    #self.application().view.show_view('Detail')
                #self.application().view.is_view_visible('Detail/DeviceChain') or self.application().view.show_view('Detail/DeviceChain')            
            
        elif self._pot_mode_index == 0: # TRACK MODE
            if self._selected_strip != None and self.selected_strip()._track != None:
                track = self.selected_strip()._track 
                mixer_names = ''
                mixer_values = ''
                
                mixer_values += self._display._adjust_strip_string(str(track.mixer_device.volume))#self.param_to_scale(track.mixer_device.volume)                
                mixer_values += self._display._adjust_strip_string(str(track.mixer_device.panning))
                
                mixer_names += self._display._adjust_strip_string(self._mixer_names[0])
                mixer_names += self._display._adjust_strip_string(self._mixer_names[1])
                
                if track != self.master_strip()._track:
                    for index in range(6):
                        if len(track.mixer_device.sends)>index:
                            mixer_values += self._display._adjust_strip_string(str(track.mixer_device.sends[index]))#self.param_to_scale(track.mixer_device.sends[index])
                            mixer_names += self._display._adjust_strip_string(self._mixer_names[index+2])
                        else:
                            mixer_values += '         '
                            mixer_names +=  '         ' 
                else:
                    mixer_names += ' '*9+'Preview  ' + ' '*9*4#' '*9*4 + 'Preview  ' + ' '*9
                    #mixer_values += ' '*9*4 + self.param_to_scale(track.mixer_device.cue_volume) + ' '*9
                    mixer_values += ' '*9+self._display._adjust_strip_string(str(track.mixer_device.cue_volume)) + ' '*9*4
                    #mixer_values += ' '*9*4 + self._display._adjust_strip_string(str(track.mixer_device.cue_volume)) + ' '*9
                    
                self._display.show_message_left(mixer_names, mixer_values, False, True)
                    
        elif self._pot_mode_index == 1: # PAN MODE
            track_names = ''
            track_pans = ''
            for index in range(7):
                track_names += self._track_names[index]
                if (self.channel_strip(index)._track):
                    track_pans += self._display._adjust_strip_string(str(self.channel_strip(index)._track.mixer_device.panning))
                else:
                    track_pans += '         '
            track_names += self._track_names[7]
            
            if self._master_mode:
                track_pans += self._display._adjust_strip_string(str(self.master_strip()._track.mixer_device.panning))
            else:
                track = self.channel_strip(7)._track
                if (track):
                    track_pans += self._display._adjust_strip_string(str(track.mixer_device.panning))
            
            self._display.show_message_left(track_names, track_pans, False, True)
        elif self._pot_mode_index < 8: # SENDS A-G MODE
            send_index = self._pot_mode_index-2
            track_names = ''
            track_sends = ''
            for index in range(7):
                #if (self._pots[index]._is_mapped) or (self._pots[index]._is_being_forwarded):
                if self.channel_strip(index)._track:
                    track_names += self._track_names[index]
                    if len(self.channel_strip(index)._track.mixer_device.sends) > send_index:
                        #track_sends += self.param_to_scale(self.channel_strip(index)._track.mixer_device.sends[send_index])
                        track_sends += self._display._adjust_strip_string(str(self.channel_strip(index)._track.mixer_device.sends[send_index]))
                    else:
                        track_sends += '         '
                else:
                    track_names += '         '
                    track_sends += '         '
            track_names += self._track_names[7]
            if not self._master_mode:
                track = self.channel_strip(7)._track 
                if track:
                    if len(track.mixer_device.sends) > send_index:
                        track_sends += self._display._adjust_strip_string(str(track.mixer_device.sends[send_index]))

            self._display.show_message_left(track_names, track_sends, False, True)
                
    def set_encoder_values(self):
        if self._encoder_mode_index == 0: #TRACK MODE
            if self._selected_strip != None and self.selected_strip()._track != None:
                track = self.selected_strip()._track 
                mixer_names = [ None for x in range(8) ] 
                self._mixer_values[0] = track.mixer_device.volume
                self._mixer_values[1] = track.mixer_device.panning
                mixer_names[0] = self._mixer_names[0]
                mixer_names[1] = self._mixer_names[1]
                for index in range(6):
                    if len(track.mixer_device.sends)>index:
                        self._mixer_values[index+2] = track.mixer_device.sends[index]
                        mixer_names[index+2] = self._mixer_names[index+2]
                    else:
                        self._mixer_values[index+2] = ''
                        mixer_names[index+2] =  ''
                if track == self.master_strip()._track:

                    mixer_names[5] =  'Tempo'
                    mixer_names[6] =  'Smooth'
                    mixer_names[7] =  'Fine'
                    tempo = self.song().tempo
                    self._mixer_values[5] = int(tempo)
                    self._mixer_values[6] = "%.1f" % tempo
                    self._mixer_values[7] = "%.2f" % tempo

                    mixer_names[3] =  'Preview'
                    #self.update_tempo_controls()
                    self._mixer_values[3] = track.mixer_device.cue_volume
                self._display.setup_left_display(mixer_names, self._mixer_values)
        elif self._encoder_mode_index == 1: # PAN MODE
            for index in range(7):
                if (self.channel_strip(index)._track):
                    self._track_pans[index] = self.channel_strip(index)._track.mixer_device.panning
                else:
                    self._track_pans[index] = ''
            if self._master_mode:
                self._track_pans[7] = self.master_strip()._track.mixer_device.panning
            else:
                track = self.channel_strip(7)._track 
                if (track):
                    self._track_pans[7] = track.mixer_device.panning
                else:
                    self._track_pans[7] = ''                
            self._display.setup_left_display(self._track_names, self._track_pans)        
        elif self._encoder_mode_index > 1 and self._encoder_mode_index < 8: # SENDS A-G MODE
            send_index = (self._encoder_mode_index-2)
            for index in range(7):
                self._track_sends[index] = ''
                if self.channel_strip(index)._track:
                    if len(self.channel_strip(index)._track.mixer_device.sends) > send_index:
                        self._track_sends[index] = self.channel_strip(index)._track.mixer_device.sends[send_index]

            self._track_sends[7] = ''
            if not self._master_mode:
                track = self.channel_strip(7)._track 
                if track:
                    if len(track.mixer_device.sends) > send_index:
                        self._track_sends[7] = track.mixer_device.sends[send_index]
            self._display.setup_left_display(self._track_names, self._track_sends)
            
        elif self._encoder_mode_index == 9: #MASTER TRACK
            if self.master_strip() and self.master_strip()._track:
                master_track = self.master_strip()._track 

                mixer_names = [ None for x in range(8) ] 

                mixer_names[0] = self._mixer_names[0]
                mixer_names[1] = self._mixer_names[1]
                mixer_names[3] =  'Preview'
                mixer_names[5] =  'Tempo'
                mixer_names[6] =  'Smooth'
                mixer_names[7] =  'Fine'
                
                self._mixer_values[0] = master_track.mixer_device.volume
                self._mixer_values[1] = master_track.mixer_device.panning 
                self._mixer_values[2] = '' 
                self._mixer_values[3] = master_track.mixer_device.cue_volume
                tempo = self.song().tempo
                self._mixer_values[4] = '' 
                self._mixer_values[5] = int(tempo)
                self._mixer_values[6] = "%.1f" % tempo
                self._mixer_values[7] = "%.2f" % tempo
                
                self._display.setup_left_display(mixer_names, self._mixer_values)
                
    def set_rel_tempo_control(self, control, smooth_control, fine_control):
        assert ((control == None) or (isinstance(control, SLEncoder) and (control.message_map_mode() is Live.MidiMap.MapMode.relative_smooth_signed_bit)))
        assert ((smooth_control == None) or (isinstance(smooth_control, SLEncoder) and (smooth_control.message_map_mode() is Live.MidiMap.MapMode.relative_smooth_signed_bit)))
        assert ((fine_control == None) or (isinstance(fine_control, SLEncoder) and (fine_control.message_map_mode() is Live.MidiMap.MapMode.relative_smooth_signed_bit)))

        if self.song().tempo_has_listener(self._on_tempo_changed):
            self.song().remove_tempo_listener(self._on_tempo_changed)   

        if (self._rel_tempo_control != None):
            self._rel_tempo_control.remove_value_listener(self._rel_tempo_value)
        self._rel_tempo_control = control
        if (self._rel_tempo_control != None):
            self._rel_tempo_control.add_value_listener(self._rel_tempo_value)

        if (self._rel_tempo_smooth_control != None):
            self._rel_tempo_smooth_control.remove_value_listener(self._rel_tempo_smooth_value)
        self._rel_tempo_smooth_control = smooth_control
        if (self._rel_tempo_smooth_control != None):
            self._rel_tempo_smooth_control.add_value_listener(self._rel_tempo_smooth_value)	

        if (self._rel_tempo_fine_control != None):
            self._rel_tempo_fine_control.remove_value_listener(self._rel_tempo_fine_value)
        self._rel_tempo_fine_control = fine_control
        if (self._rel_tempo_fine_control != None):
            self._rel_tempo_fine_control.add_value_listener(self._rel_tempo_fine_value)

        if (self._rel_tempo_control != None) and (self._rel_tempo_fine_control != None) and (self._rel_tempo_smooth_control != None):
            self.song().add_tempo_listener(self._on_tempo_changed)
            self._tempo_control_update_count = 1
        else:
            self._tempo_control_update_count = -1
        self.update()

    def _rel_tempo_value(self, value):
        assert (self._rel_tempo_control != None)
        assert (value in range(128))
        if self.is_enabled():
            tempo = self.song().tempo
            if round(tempo) == tempo:
                if value < 30:
                    increment = 1#value
                else:
                    increment = -1#-(value-64) 
                new_tempo = min(self._tempo_top, max(self._tempo_bottom, tempo+increment))
            else:
                if value < 30:
                    new_tempo = min(self._tempo_top, max(self._tempo_bottom, int(tempo)+1))
                else:
                    new_tempo = min(self._tempo_top, max(self._tempo_bottom, int(tempo)))		

            self.song().tempo = int(new_tempo)

    def _rel_tempo_smooth_value(self, value):
        assert (self._rel_tempo_smooth_control != None)
        assert (value in range(128))
        if self.is_enabled():
            fraction = ((self._tempo_top - self._tempo_bottom) / 256.0)
            if value < 30:
                increment = 1#value
            else:
                increment = -1#-(value-64) 
            new_tempo = min(self._tempo_top, max(self._tempo_bottom, self.song().tempo+(fraction*increment)))
            self.song().tempo = new_tempo

    def _rel_tempo_fine_value(self, value):
        assert (self._rel_tempo_fine_control != None)
        assert (value in range(128))
        if self.is_enabled():
            if value < 30:
                increment = value
            else:
                increment = -(value-64)
            #self.song().tempo += 0.01*increment

            new_tempo = min(self._tempo_top, max(self._tempo_bottom, self.song().tempo+(0.01*increment)))
            self.song().tempo = new_tempo       
       
    def _on_tempo_changed(self):
        self.set_encoder_values()
        self.update_tempo_controls()
        self._tempo_control_update_count = 10

    def update_tempo_controls(self):
        if self._support_mkII and self._rel_tempo_control != None and self._rel_tempo_fine_control != None and self._rel_tempo_smooth_control != None:

            self._rel_tempo_control._ring_mode_button.send_value(64, True)
            self._rel_tempo_smooth_control._ring_mode_button.send_value(64, True)
            self._rel_tempo_fine_control._ring_mode_button.send_value(64, True)	

            value = self.song().tempo%11+1
            self._rel_tempo_control._led_ring_encoder.send_value(int(value), True)
            #value = (self.song().tempo*10)%11+1
            self._rel_tempo_smooth_control._led_ring_encoder.send_value(int(value), True) 
            self._rel_tempo_fine_control._led_ring_encoder.send_value(int(value), True) 	    

    def _on_custom_timer(self):
        if self._support_mkII and self._tempo_control_update_count > -1:
            if self._tempo_control_update_count == 8:
                self.update_tempo_controls()
            elif self._tempo_control_update_count == 4:
                self._rel_tempo_control._led_ring_encoder.send_value(0, True)
                self._rel_tempo_smooth_control._led_ring_encoder.send_value(0, True)
                self._rel_tempo_fine_control._led_ring_encoder.send_value(0, True)
            self._tempo_control_update_count -= 1
            if self._tempo_control_update_count == 0:
                self._tempo_control_update_count = 8
                
        if self._pot_moved:
            self._pot_moved = False
            self.show_pot_values()
        
    def on_selected_track_changed(self):
        if SMART_VIEW and self._selected_strip != None:
            old_track = self.selected_strip()._track
            if old_track and old_track in self.song().tracks:
                if old_track.playing_slot_index_has_listener(self._on_selected_track_playing_slot_changed):
                    old_track.remove_playing_slot_index_listener(self._on_selected_track_playing_slot_changed)
        
        MixerComponent.on_selected_track_changed(self)
        
        if SMART_VIEW and self._selected_strip != None and (not self.song().select_on_launch):
            new_track = self.selected_strip()._track
            if new_track and new_track in self.song().tracks:
                if not new_track.playing_slot_index_has_listener(self._on_selected_track_playing_slot_changed):
                    new_track.add_playing_slot_index_listener(self._on_selected_track_playing_slot_changed)
        
        if self._encoder_mode_index == 0: #track mode
            self.set_encoder_values()
        self.update_selected_tracks_string()
            
    def _on_selected_track_playing_slot_changed(self):
        if SMART_VIEW:# and self.application().view.is_view_visible('Detail/Clip'):
            track = self.song().view.selected_track
            if track in self.song().tracks: #except return and master tracks
                playing_index = track.playing_slot_index
                #fired_index = track.fired_slot_index
                #if fired_index > -1:
                    #playing_index = fired_index
                current_index = self._session._scene_offset 
                if playing_index > -1: 
                    self.song().view.selected_scene = self.song().scenes[playing_index]
                else:
                    self.song().view.selected_scene = self.song().scenes[current_index] 
                    
                #if self.song().view.highlighted_clip_slot.has_clip and not self.application().view.is_view_visible('Detail/Clip'):
                    #self.application().view.show_view('Detail/Clip')                      
            #SELECTING SCENE
            #selected_scene = self.song().view.selected_scene
            #all_scenes = self.song().scenes
            #index = list(all_scenes).index(selected_scene)
            #self._session.set_offsets(self._session._track_offset, index)
                    
class SLMixerStrip(ChannelStripComponent):
    ' Subclass of channel strip component using select button for (un)folding tracks '

    def __init__(self, mixer, session):
        self._mixer = mixer
        self._session = session
        self._select_button_pressed = False
        self._select_button_pressed_time = 0   
        self._select_button_double_press = 0
        self._volume_control_1 = None
        self._volume_control_2 = None
        self._cue_volume_control = None
        self._cue_volume_control_2 = None
        self._pan_control_2 = None
        self._send_controls_2 = []
        ChannelStripComponent.__init__(self)
        self._register_timer_callback(self._on_custom_timer)
        self._last_beat = -1

    def disconnect(self):
        self._unregister_timer_callback(self._on_custom_timer)
        if (self._track != None):
            if (self._volume_control_1 != None):
                self._volume_control_1.release_parameter()
                self._volume_control_1 = None             
            if (self._volume_control_2 != None):
                self._volume_control_2.release_parameter()
                self._volume_control_2 = None  
            if (self._cue_volume_control != None):
                self._cue_volume_control.release_parameter()
                self._cue_volume_control = None
            if (self._cue_volume_control_2 != None):
                self._cue_volume_control_2.release_parameter()
                self._cue_volume_control_2 = None
            if (self._pan_control_2 != None):
                self._pan_control_2.release_parameter()
                self._pan_control_2 = None   
            if (self._send_controls_2 != None):
                for send_control in self._send_controls_2:
                    if (send_control != None):
                        send_control.release_parameter()
                self._send_controls_2 = None            
        ChannelStripComponent.disconnect(self)

    def set_select_button(self, button):
        ChannelStripComponent.set_select_button(self, button)
        self._select_button_pressed = False
        self._select_button_pressed_time = 0

    def set_arm_button(self, button):
        #assert (self._track != self.song().master_track)
        #assert ((button == None) or isinstance(button, ButtonElement))
        if (button != self._arm_button):
            if (self._arm_button != None):
                self._arm_button.remove_value_listener(self._arm_value)
                self._arm_button.reset()
            #if self.song().current_song_time_has_listener(self._on_song_time_changed):
                #self.song().remove_current_song_time_listener(self._on_song_time_changed)
            #if self.song().is_playing_has_listener (self._on_playing_status_changed):
                #self.song().remove_is_playing_listener(self._on_playing_status_changed)
            self._arm_pressed = False #added
            self._arm_button = button
            if (self._arm_button != None):
                self._arm_button.add_value_listener(self._arm_value)
                #self.song().add_current_song_time_listener(self._on_song_time_changed)
                #self.song().add_is_playing_listener(self._on_playing_status_changed)
            self.update()

    def _select_value(self, value):
        #ChannelStripComponent._select_value(self, value)
        assert (self._select_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if (self._track != None):
                if ((value != 0) or (not self._select_button.is_momentary())):
                    if (self.song().view.selected_track != self._track):
                        self.song().view.selected_track = self._track
                        self.on_selected_track_changed()
                        self._mixer.update_selected_tracks_string()
                        #SMART VIEW - TRACK CHANGED
                        self._mixer._on_selected_track_playing_slot_changed()
                        #if SMART_VIEW:
                            #if self.application().view.is_view_visible('Detail/DeviceChain'):
                                #self.song().view.selected_scene = self.song().scenes[current_index]
                            #elif self.application().view.is_view_visible('Detail/Clip'):
                                #if playing_index > -1: # and self._track in self.song().tracks
                                    #self.song().view.selected_scene = self.song().scenes[playing_index]
                                #else:
                                    #self.song().view.selected_scene = self.song().scenes[current_index]
                        if (self._mixer._device.is_enabled() and not self._mixer._device._locked_to_device) or (self._mixer._extra_device and self._mixer._extra_device.is_enabled() and not self._mixer._extra_device._locked_to_device):
                            pass #show device
                        else:
                            self._mixer.show_selected_tracks()

                    else:
                        #SMART VIEW - TRACK NOT CHANGED
                        if SMART_VIEW and (self.song().view.selected_track in self.song().tracks):
                            playing_index = -1
                            if self._track in self.song().tracks: #except return and master tracks
                                playing_index = self._track.playing_slot_index
                                fired_index = self._track.fired_slot_index
                                if fired_index > -1:
                                    playing_index = fired_index
                            current_index = self._session._scene_offset                            
                            #if self.application().view.is_view_visible('Detail/DeviceChain'):
                                #if self.song().view.selected_scene != self.song().scenes[current_index]:
                                    #self.song().view.selected_scene = self.song().scenes[current_index]
                            if self.application().view.is_view_visible('Detail/Clip'):
                                if playing_index > -1 and self.song().view.selected_scene != self.song().scenes[playing_index]:
                                    self.song().view.selected_scene = self.song().scenes[playing_index]
                                elif self.song().view.selected_track.clip_slots[current_index].has_clip:
                                    self.song().view.selected_scene = self.song().scenes[current_index]                                
                        self._mixer.show_selected_tracks(True)
                        
                        #============== DEVICE SELECT TEST ==============================
                        
                        ##device_names = ''
                        #devices = self.song().view.selected_track.devices
                        ##if devices:
                            ##device_count = len(devices)
                            ##for device in devices:
                                ##device_names += self._display._adjust_strip_string(device.name)
                        ##self._display.show_message_left(device_names)                        
                        #if devices:
                            #device_count = len(devices)
                            ##self._device.set_device(devices[device_count-1])
                            
                            ##self.song().view.select_device(devices[device_count-1])  
                            ##self.song().view.select_device(devices[0]) 
                            
                        #============== DEVICE SELECT TEST ==========================
                        
                    
                    if self._select_button_double_press > 0:
                        if self._track.can_be_armed:
                            for track in self.song().tracks: #added
                                if track.can_be_armed:
                                    if (track == self._track):
                                        track.arm = True
                                    else:
                                        track.arm = False
                            self._mixer.show_arm_values(True)
                        self._select_button_double_press = 0
                    else:
                        self._select_button_double_press = BUTTON_DOUBLE_PRESS_DELAY
                    self._select_button_pressed = True
                else:
                    self._select_button_pressed = False
                    self._select_button_pressed_time = 0                    

    def _arm_value(self, value):
        assert (self._arm_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if self._track != None:
                if self._track.can_be_armed:
                    self._arm_pressed = ((value != 0) and self._arm_button.is_momentary())
                    if (not self._arm_button.is_momentary()) or (value != 0):
                        expected_arms_pressed = 0
                        if self._arm_pressed:
                            expected_arms_pressed = 1
                        arm_exclusive = (self.song().exclusive_arm != self._shift_pressed) and ((not self._arm_button.is_momentary()) or (ChannelStripComponent.number_of_arms_pressed() == expected_arms_pressed))
                        new_value = not self._track.arm #added
                        respect_multi_selection = self._track.is_part_of_selection #added
                        for track in self.song().tracks: #added
                            if track.can_be_armed:
                                if (track == self._track) or (respect_multi_selection and track.is_part_of_selection): #added
                                    track.arm = new_value #added
                                    if TRACK_SELECT_ON_ARM and self._track.arm:# self.song().view.selected_track != self._track:
                                        self.song().view.selected_track = self._track                                
                                elif arm_exclusive and track.arm: #added
                                    track.arm = False #added
                self._mixer.show_arm_values()

    def _mute_value(self, value):
        assert (self._mute_button != None)
        assert isinstance(value, int)
        if self.is_enabled():
            if ((not self._mute_button.is_momentary()) or (value != 0)):
                if ((self._track != None) and (self._track != self.song().master_track)):
                    self._track.mute = (not self._track.mute)   
                self._mixer.show_mute_values()

    def _solo_value(self, value):
        ChannelStripComponent._solo_value(self, value)
        assert (self._solo_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if ((value != 0) or (not self._solo_button.is_momentary())):
                self._mixer.show_solo_values()

    def set_track(self, track):
        #assert ((track == None) or isinstance(track, Live.Track.Track))
        if not isinstance(track, (type(None), Live.Track.Track)): 
            raise AssertionError
            if (self._volume_control_1 != None):
                self._volume_control_1.release_parameter()
            if (self._volume_control_2 != None):
                self._volume_control_2.release_parameter()
            if (self._cue_volume_control != None):
                self._cue_volume_control.release_parameter()
            if (self._cue_volume_control_2 != None):
                self._cue_volume_control_2.release_parameter()
            if (self._pan_control_2 != None):
                self._pan_control_2.release_parameter()
            if (self._send_controls_2 != None):
                for send_control in self._send_controls_2:
                    if (send_control != None):
                        send_control.release_parameter()
        ChannelStripComponent.set_track(self, track)
        

    def set_volume_control_1(self, control):
        assert ((control == None) or isinstance(control, EncoderElement))
        if (control != self._volume_control_1):
            self._volume_control_1 = control
            self.update()  
            
    def set_volume_control_2(self, control):
        assert ((control == None) or isinstance(control, EncoderElement))
        if (control != self._volume_control_2):
            self._volume_control_2 = control
            self.update()            

    def set_cue_volume_control(self, control):
        assert ((control == None) or isinstance(control, EncoderElement))
        if (control != self._cue_volume_control):
            self._cue_volume_control = control
            self.update()

    def set_cue_volume_control_2(self, control):
        assert ((control == None) or isinstance(control, EncoderElement))
        if (control != self._cue_volume_control_2):
            self._cue_volume_control_2 = control
            self.update()
            
    def set_pan_control_2(self, control):
        assert ((control == None) or isinstance(control, EncoderElement))
        if (control != self._pan_control_2):
            self._pan_control_2 = control
            self.update()

    def set_send_controls_2(self, controls):
        assert ((controls == None) or isinstance(controls, tuple))
        if (controls != self._send_controls_2):
            self._send_controls_2 = controls
            self.update()
            
    def update(self):
        if self._allow_updates:
            if self.is_enabled():
                if (self._track != None):
                    if (self._volume_control_1 != None):
                        self._volume_control_1.connect_to(self._track.mixer_device.volume)
                    if (self._volume_control_2 != None):
                        self._volume_control_2.connect_to(self._track.mixer_device.volume)
                    if (self._pan_control_2 != None):
                        self._pan_control_2.connect_to(self._track.mixer_device.panning)
                    if (self._cue_volume_control != None):
                        self._cue_volume_control.connect_to(self.song().master_track.mixer_device.cue_volume)  
                    if (self._cue_volume_control_2 != None):
                        self._cue_volume_control_2.connect_to(self.song().master_track.mixer_device.cue_volume)
                    if (self._send_controls_2 != None):
                        index = 0
                        for send_control in self._send_controls_2:
                            if (send_control != None):
                                if (index < len(self._track.mixer_device.sends)):
                                    send_control.connect_to(self._track.mixer_device.sends[index])
                                else:
                                    send_control.release_parameter()
                            index += 1                    
            else:
                if (self._track != None):
                    if (self._volume_control_1 != None):
                        self._volume_control_1.release_parameter()
                    if (self._volume_control_2 != None):
                        self._volume_control_2.release_parameter() 
                    if (self._pan_control_2 != None):
                        self._pan_control_2.release_parameter()  
                    if (self._send_controls_2 != None):
                        for send_control in self._send_controls_2:
                            if (send_control != None):
                                send_control.release_parameter()
                if (self._cue_volume_control != None):
                    self._cue_volume_control.release_parameter()
                if (self._cue_volume_control_2 != None):
                    self._cue_volume_control_2.release_parameter()
        ChannelStripComponent.update(self)

    #def _on_song_time_changed(self):
        #if self._allow_updates:
            #if (self.is_enabled() and (self._arm_button != None)):
                #curr_song_beat = int(self.song().current_song_time % 2)
                #if self._last_beat != curr_song_beat:
                    #if ((self._track != None) and ((self._track in self.song().tracks) and (self._track.can_be_armed and self._track.arm))):
                        #if self._track.playing_slot_index > -1 and self._track.clip_slots and self.song().is_playing:
                            #recording = False
                            #for slot in self._track.clip_slots:
                                ##if slot.has_clip and (slot.clip.is_recording or slot.clip.is_overdubbing):
                                    ##recording = True
                                    ##break
                                #if slot.has_clip:
                                    #if slot.clip.is_playing:
                                        #if slot.clip.is_recording or slot.clip.is_overdubbing:
                                            #recording = True
                                        #break
                            #if curr_song_beat == 1 or not recording:
                                #self._arm_button.turn_on()
                            #else:
                                #self._arm_button.turn_off()
                        #else:
                            #self._arm_button.turn_on()
                            #self._last_beat = -1
                    #else:
                        #self._arm_button.turn_off()
                        #self._last_beat = -1
                    #self._last_beat = curr_song_beat
                
    #def _on_playing_status_changed(self):
        #if self.is_enabled():
            #self._last_beat = -1
            #self._on_song_time_changed()
        
    def _on_custom_timer(self):
        if self.is_enabled():
            if (self._select_button_double_press > 0):
                self._select_button_double_press -= 1              
            if SMART_VIEW and self._select_button_pressed:
                self._select_button_pressed_time += 1
                if self._select_button_pressed_time > 6:
                    if self._select_button_pressed_time == BUTTON_HOLD_DELAY:
                        if self._track != None and self._track.is_foldable:
                            self._track.fold_state = not self._track.fold_state
                        #if self.application().view.is_view_visible('Detail/DeviceChain'):
                            #self.application().view.show_view('Detail/Clip')
                            #self._mixer._on_selected_track_playing_slot_changed()
                            #if (self.song().view.follow_song == False):
                                #self.song().view.follow_song = True
                        #else:
                            #self.application().view.show_view('Detail/DeviceChain')


    def _on_mute_changed(self): #support_mkII
        if self.is_enabled() and self._mute_button != None and self._mixer._support_mkII:
            if self._track != None or self.empty_color == None:
                if self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.mute != self._invert_mute_feedback:
                    self._mute_button.turn_on()
                else:
                    self._mute_button.turn_off()
            else:
                self._mute_button.set_light(self.empty_color)
                
    def _on_solo_changed(self): #support_mkII
        if self.is_enabled() and self._solo_button != None and self._mixer._control_second_row and self._mixer._support_mkII:
            if self._track != None or self.empty_color == None:
                if self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.solo:
                    self._solo_button.turn_on()
                else:
                    self._solo_button.turn_off()
            else:
                self._solo_button.set_light(self.empty_color)
                
    def _on_arm_changed(self): #support_mkII
        if self.is_enabled() and self._arm_button != None and self._mixer._support_mkII:
            if self._track != None and self._track in self.song().tracks and self._track.can_be_armed and self._track.arm:
                self._arm_button.turn_on()
            else:
                self._arm_button.turn_off()
                
    def on_selected_track_changed(self): #support_mkII
        if self.is_enabled() and self._select_button != None and self._mixer._support_mkII:
            if self._track != None or self.empty_color == None:
                if self.song().view.selected_track == self._track:
                    self._select_button.turn_on()
                else:
                    self._select_button.turn_off()
            else:
                self._select_button.set_light(self.empty_color)