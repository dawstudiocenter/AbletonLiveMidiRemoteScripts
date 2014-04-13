import Live
#from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector 
from _Framework.ButtonElement import ButtonElement
from config import P2_INVERT_SHIFT_MODE

class SLMasterModeSelector(ChannelTranslationSelector):
    __doc__ = ' SelectorComponent that assigns buttons to functions based on the mixer mode buttons '
    def __init__(self, mixer, session, sliders, button_modes, shift_mode, encoder_modes, pot_modes):
        assert len(sliders) == 8
        ChannelTranslationSelector.__init__(self)
        self._master_mode = False
        self._master_mode_button = None
        self._sliders = sliders
        self._mixer = mixer
        self._session = session
        self._button_modes = button_modes
        self._shift_mode = shift_mode
        self._encoder_modes = encoder_modes
        self._pot_modes = pot_modes

        self.update_master_mode_button()
        self.set_mode(0)

    def disconnect(self):
        ChannelTranslationSelector.disconnect(self)
        if (self._master_mode_button != None):
            self._master_mode_button.remove_value_listener(self.master_mode_value)
            self._master_mode_button = None       
        self._mixer = None
        self._sliders = None
        #self._mode_button = None
        return None

    def number_of_modes(self):
        return 2

    def update(self):
        #ChannelTranslationSelector.update(self)
        self._mixer.master_strip().set_volume_control_1(None)
        for index in range(8):
            strip = self._mixer.channel_strip(index)
            strip.set_volume_control_1(None)
            self._sliders[index].release_parameter()

        self._mixer._reassign_tracks()
            
        for index in range(7):
            strip = self._mixer.channel_strip(index)
            slider = self._sliders[index]
            strip.set_volume_control_1(slider)
            
        if self._master_mode:
            self._mixer.master_strip().set_volume_control_1(self._sliders[7])
        else:
            self._mixer.channel_strip(7).set_volume_control_1(self._sliders[7])

        self.update_master_mode_button()
        return None

    def set_master_mode_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._master_mode_button != button):
            if (self._master_mode_button != None):
                self._master_mode_button.remove_value_listener(self.master_mode_value)
                self._master_mode_button.reset()
            self._master_mode_button = button
            if (self._master_mode_button != None):
                self._master_mode_button.add_value_listener(self.master_mode_value)
                self.update_master_mode_button()#self._master_mode_button.reset()

    def master_mode_value(self, value):
        assert (self._master_mode_button != None)
        assert (value in range (128))

        if ((value is not 0) or (not self._master_mode_button.is_momentary())):
            self._master_mode = not self._master_mode
            self.set_mode(int(self._master_mode))
            self.update_master_mode()
            self._mixer._display.set_block_right(False)            
        self.update_master_mode_button()
        self._session.update()
        
    def update_master_mode(self):
        assert (self._master_mode_button != None)
        
        self.update()
        
        self._mixer._master_mode = self._master_mode
        self._mixer.update_track_names()
        #self._mixer._display.set_block_right(False)
        self._mixer.set_slider_values()
        
        self._session._master_mode = self._master_mode
        self._session.track_increment = 1 + ((7-int(self._master_mode))*(int(not P2_INVERT_SHIFT_MODE ^ self._session._shift_button.is_pressed())))
        self._session.update()
        self._session._do_show_highlight()
        
        self._button_modes._master_mode = self._master_mode
        self._button_modes.update_master_mode()
        
        self._shift_mode._master_mode = self._master_mode
        self._shift_mode.update_master_mode()
        
        self._encoder_modes._master_mode = self._master_mode
        self._encoder_modes.update_master_mode()
        self._mixer.set_encoder_values()
        
        self._pot_modes._master_mode = self._master_mode
        self._pot_modes.update_master_mode()        
        
        #self.update_master_mode_button()
        
    def update_master_mode_button(self):
        if (self._master_mode_button != None):
            if self._master_mode:# and (self._master_mode_button.is_pressed() or self._mixer._shift_pressed):
                self._master_mode_button.turn_on()
            else:
                self._master_mode_button.turn_off()
    def on_track_list_changed(self):
        self.update()
        return None            
    
    
    
    