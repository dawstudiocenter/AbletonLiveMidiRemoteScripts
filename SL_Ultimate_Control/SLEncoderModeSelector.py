import Live 
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector 
from _Framework.ButtonElement import ButtonElement 
from config import DEFAULT_ENCODER_MODE, SMART_VIEW
from consts import BUTTON_HOLD_DELAY

class SLEncoderModeSelector(ChannelTranslationSelector):
    ' SelectorComponent that assigns select buttons to different functions '

    def __init__(self, mixer, device, encoders):
        ChannelTranslationSelector.__init__(self)
        self._master_mode = False
        self._mode_names = [' TRACK*  ','  PAN    ',' SEND A  ',' SEND B  ',' SEND C  ',' SEND D  ',' SEND E  ',' SEND F  ',' DEVICE  ',' MASTER TRACK ']
        self._mixer = mixer
        self._device = device
        self._encoders = encoders
        self._track_mode_pressed_time = 0

        self.set_mode(DEFAULT_ENCODER_MODE)
        
        
        #self._modes_buttons.index(sender)
        self._register_timer_callback(self._on_custom_timer)

    def disconnect(self):
        self._unregister_timer_callback(self._on_custom_timer)
        ChannelTranslationSelector.disconnect(self)
        self._mixer = None
        self._device = None
        self._encoders = None
        
    def _on_custom_timer(self):
        if self.is_enabled():
            #if self._stop_button_blink:
                #if self._stop_button_feedback != None and not self.song().is_playing:
                    #self._stop_button_feedback.turn_on()
                #self._stop_button_blink = False
            if self._modes_buttons and self._modes_buttons[0] and self._modes_buttons[0].is_pressed():
                self._track_mode_pressed_time += 1
                if self._track_mode_pressed_time == BUTTON_HOLD_DELAY:
                    self.set_mode(9)
                    self.show_modes()
                    #self._mixer._display.show_message_left('TEST')
                    pass
                    #self._stop_button_feedback.turn_off()
                    #self.song().stop_all_clips()
                    #self._stop_button_blink = True                    
            
    def set_mode_buttons(self, buttons):
        assert isinstance(buttons, (tuple,
                                    type(None)))
        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)
        self._modes_buttons = []
        self._track_mode_pressed_time = 0 
        if (buttons != None):
            index = 0
            for button in buttons:
                assert isinstance(button, ButtonElement)
                identify_sender = True
                button.add_value_listener(self._mode_value, identify_sender)
                self._modes_buttons.append(button)
                if (index == self._mode_index):
                    self._modes_buttons[index].turn_on()
                else:
                    self._modes_buttons[index].turn_off()
                index += 1

    def number_of_modes(self):
        return 10

    def update(self):
        #ChannelTranslationSelector.update(self)
        if self.is_enabled():
            assert (self._mode_index in range(self.number_of_modes()))

            self._mixer._encoder_mode_index = self._mode_index
            self._mixer._reassign_tracks()
            
            for index in range(len(self._modes_buttons)):
                if (index == self._mode_index):
                    self._modes_buttons[index].turn_on()
                else:
                    self._modes_buttons[index].turn_off()
                        
            self._device.set_enabled(0)                    
            self._device.set_parameter_controls(None)
            #if self._device._on_off_button != None:
                #self._device._on_off_button.turn_off()

            self._mixer.selected_strip().set_pan_control(None)
            self._mixer.selected_strip().set_volume_control(None)
            self._mixer.selected_strip().set_cue_volume_control(None)
            self._mixer.selected_strip().set_send_controls((None, None, None, None, None, None))

            for index in range(8):
                strip = self._mixer.channel_strip(index)
                encoder = self._encoders[index]
                strip.set_volume_control(None)
                strip.set_pan_control(None)
                strip.set_send_controls((None, None, None, None, None, None))
                strip.set_cue_volume_control(None)
                encoder.release_parameter()

            self._mixer.master_strip().set_volume_control(None)
            self._mixer.master_strip().set_pan_control(None)
            self._mixer.master_strip().set_cue_volume_control(None)
            self._mixer.master_strip().set_send_controls((None, None, None, None, None, None))

            self._encoders[7].release_parameter()
            self._mixer.set_rel_tempo_control(None, None, None)

            send_controls = [None, None, None, None, None, None, None]

            if (self._mode_index == 0): #TRACK MODE
                # pan control
                self._mixer._selected_strip.set_volume_control(self._encoders[0])
                self._mixer._selected_strip.set_pan_control(self._encoders[1])
                # sends control
                if self._mixer.selected_strip()._track != self._mixer.master_strip()._track: #NOT MASTER TRACK
                    snd_ctr = [self._encoders[index+2] for index in range(6)]
                    self._mixer._selected_strip.set_send_controls(tuple(snd_ctr))
                else: # MASTER TRACK
                    self._mixer.set_rel_tempo_control(self._encoders[5], self._encoders[6], self._encoders[7])
                    self._mixer._selected_strip.set_cue_volume_control(self._encoders[3])

            elif (self._mode_index == 1): #PAN MODE
                for index in range(7):
                    strip = self._mixer.channel_strip(index)
                    encoder = self._encoders[index]
                    strip.set_pan_control(encoder)
                #self._mixer.master_strip().set_pan_control(self._encoders[7])
                
            elif (self._mode_index < 8): #SENDS A-F MODE  
                for index in range(7):
                    strip = self._mixer.channel_strip(index)
                    encoder = self._encoders[index]
                    send_controls = [None, None, None, None, None, None, None]
                    send_controls[self._mode_index-2] = encoder
                    strip.set_send_controls(tuple(send_controls))
                    
            elif (self._mode_index == 8): #DEVICE MODE    
                self._device.set_enabled(1) 
                self._device.set_parameter_controls(self._encoders)
                if not self._device._device:
                    self.song().view.selected_track.view.select_instrument()
                    #devices = self.song().view.selected_track.devices
                    #device_count = len(devices)
                    #if device_count > 0 : #track has devices, but device not selected
                        #self.song().view.select_device(devices[0]) #select first device                
                self._device.update()#self._device.on_enabled_changed()
                #self._device.show_device()
                self._device.show_device_parameters() 
                
            if (self._mode_index == 9): #MASTER TRACK
                master_strip = self._mixer.master_strip()
                
                master_strip.set_volume_control(self._encoders[0])
                master_strip.set_pan_control(self._encoders[1])
                master_strip.set_cue_volume_control(self._encoders[3])
                self._mixer.set_rel_tempo_control(self._encoders[5], self._encoders[6], self._encoders[7])
                
            self.update_master_mode()
            
    def update_master_mode(self):
        strip = self._mixer.channel_strip(7)
        encoder = self._encoders[7]
        if (self._mode_index == 0): #TRACK MODE
            pass
        
        elif (self._mode_index == 8): #DEVICE MODE    
            pass

        elif (self._mode_index == 1): #PAN MODE
            encoder.release_parameter()  
            if self._master_mode:
                strip.set_pan_control(None)
                self._mixer.master_strip().set_pan_control(encoder)
            else:
                self._mixer.master_strip().set_pan_control(None)
                strip.set_pan_control(encoder)
            
        elif (self._mode_index < 8): #SENDS A-F MODE
            encoder.release_parameter()  
            send_controls = [None, None, None, None, None, None, None]
            if self._master_mode:
                pass
            else:
                #self._mixer.master_strip().set_send_controls(send_controls)
                send_controls[self._mode_index-2] = encoder
            strip.set_send_controls(tuple(send_controls))            


    def _mode_value(self, value, sender):
        ChannelTranslationSelector._mode_value(self, value, sender)
        if ((value != 0) or (not sender.is_momentary())):
            if (self._mode_index != 8):
                self.show_modes()
            else:
                self._device.show_device_parameters()
        else:
            self._track_mode_pressed_time = 0 

    def show_modes(self):
        mode_names = ''
        for index in range(self.number_of_modes()-1):
            if self._mode_index != index:
                mode_names += self._mode_names[index]
            else:
                if index != 0:
                    mode_names = mode_names[:-1] + '['
                mode_names += self._mode_names[index][:-1]+']'
        self._mixer._display.show_message_left(' Encoder Mode: '+self._mode_names[self._mode_index].strip(), mode_names)
            
    def on_selected_track_changed(self):
        #ModeSelectorComponent.on_selected_track_changed(self)
        if (self._mode_index == 0): #track mode
            self.update() 
        return None
    
    #def on_track_list_changed(self):
        #self.update()
        #return None