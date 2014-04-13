import Live
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement

from SL_Ultimate_Extra_Device_Browser.SLExtraDeviceControl import SLExtraDeviceControl
from SLBrowserControl import *
from config import BROWSER_ENABLE

class SLShiftableSelector(ModeSelectorComponent):
    __doc__ = ' Selector that assigns buttons to functions based on the shift button '
    def debug(self,msg):
        return self._parent.log(msg)
        
    def __init__(self, select_buttons, show_pot_values_button, p1buttons, scene_up_button, scene_down_button, scene_launch_button, session, mixer, encoder_modes, device, device_control, clip_launch_buttons, pot_modes, pad_buttons = None, pot_encoders = None, parent=None):
        assert len(select_buttons) == 8
        if BROWSER_ENABLE:
            assert len(pad_buttons) == 8
            assert len(pot_encoders) == 8
        self._parent = parent
        ModeSelectorComponent.__init__(self)
        self._master_mode = False
        self._toggle_pressed = False
        self._select_buttons = select_buttons
        self._show_pot_values_button = show_pot_values_button
        self._scene_up_button = scene_up_button
        self._scene_down_button = scene_down_button 
        self._scene_launch_button = scene_launch_button
        self._clip_launch_buttons = clip_launch_buttons
        if BROWSER_ENABLE:
            self._pad_buttons = pad_buttons
            self._pot_encoders = pot_encoders
        self._encoder_mode_buttons = self._select_buttons + (self._scene_up_button,)
        self._p1buttons = p1buttons
        self._encoder_modes = encoder_modes
        self._pot_modes = pot_modes
        self._pot_mode_buttons = None
        self._session = session
        self._mixer = mixer
        self._device = device
        self._device_control = device_control
        
    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._select_buttons = None
        if BROWSER_ENABLE:
            self._pad_buttons = None
        self._show_pot_values_button = None
        self._encoder_modes = None
        self._slider_modes = None
        self._mixer = None
        self._device = None
        return None

    def set_mode_toggle(self, button):
        ModeSelectorComponent.set_mode_toggle(self, button)
        self.set_mode(0)

    def number_of_modes(self):
        return 2

    def update(self):
        if self.is_enabled():
            
            if (self._mode_index == 0):
                #self.debug('UNSHIFT')
                #UNSHIFTED
                self._encoder_modes.set_mode_buttons(None)
                self._pot_modes.set_mode_buttons(None)
                
                self._device.set_bank_nav_buttons(None, None)
                
                self._device.set_on_off_button(None)
                self._device.set_lock_button(None)
                
                self._device_control.set_device_nav_buttons(self._p1buttons[1], self._p1buttons[0]) 

                if SLBrowserControl._device:
                    #SLBrowserControl._device.set_lock_button(None) 
                    #SLBrowserControl._device.set_on_off_button(None)
                    SLBrowserControl._device.set_action_controls(self._pad_buttons)
                    SLBrowserControl._device.set_parameter_controls(self._pot_encoders)
                    
                if SLExtraDeviceControl._device:
                    SLExtraDeviceControl._device.set_lock_button(None) 
                    SLExtraDeviceControl._device.set_on_off_button(None) 
                    
                self._mixer.set_show_pot_values_button(self._show_pot_values_button)
                self._session.set_scene_bank_buttons(self._scene_down_button, self._scene_up_button)
                self._session.scene(0).set_launch_button(self._scene_launch_button)
                for index in range(7):
                    self._mixer.channel_strip(index).set_select_button(self._select_buttons[index]) 
                    clip_slot = self._session.scene(0).clip_slot(index)
                    clip_slot.set_launch_button(self._clip_launch_buttons[index])
                    clip_slot.set_triggered_to_play_value(0)
                self.update_master_mode()
                
                self._mixer._display.set_block_left(False)
                #self._mixer._display.set_block_right(False)
                self._mode_toggle.turn_off()
            elif (self._mode_index == 1):
                #self.debug('SHIFT')
                #SHIFTED
                self._session.scene(0).set_launch_button(None)                
                for index in range(8):
                    self._mixer.channel_strip(index).set_select_button(None)
                    clip_slot = self._session.scene(0).clip_slot(index)
                    clip_slot.set_launch_button(None)
                self._mixer.master_strip().set_select_button(None) 
                self._session.set_show_scene_button(None)
                
                self._device_control.set_device_nav_buttons(None, None) 

                self._session.set_scene_bank_buttons(None, None)
                self._mixer.set_show_pot_values_button(None)
                
                self._device.set_bank_nav_buttons(self._p1buttons[1], self._p1buttons[0])
                
                self._device.set_on_off_button(self._scene_down_button)
                self._device.set_lock_button(self._scene_up_button)
                self._encoder_modes.set_mode_buttons(self._encoder_mode_buttons)  
                
                
                if SLExtraDeviceControl._device:
                    self._pot_mode_buttons = self._clip_launch_buttons + (self._scene_launch_button,)
                    SLExtraDeviceControl._device.set_lock_button(self._scene_launch_button)
                    SLExtraDeviceControl._device.set_on_off_button(self._show_pot_values_button) 
                if BROWSER_ENABLE and SLBrowserControl._device:                    
                    self._pot_mode_buttons = self._clip_launch_buttons + (self._scene_launch_button,) + self._pad_buttons
                    #SLBrowserControl._device.set_lock_button(self._scene_launch_button)
                    #SLBrowserControl._device.set_on_off_button(self._show_pot_values_button) 
                    SLBrowserControl._device.set_action_controls(None)
                    SLBrowserControl._device.set_parameter_controls(None)
                else:
                    self._pot_mode_buttons = self._clip_launch_buttons + (self._scene_launch_button,)               
                self._pot_modes.set_mode_buttons(self._pot_mode_buttons)
                
                #if (self._encoder_modes._mode_index == 8):
                if self._device.is_enabled():
                    #self._device.show_device()
                    self._device.show_device_parameters()
                else:
                    self._encoder_modes.show_modes()
                self._mixer._display.set_block_left(True)
                self._mode_toggle.turn_on()
            else:
                assert False
        return None

    def _toggle_value(self, value):
        assert self._mode_toggle != None
        assert value in range(128)
        self._toggle_pressed = value > 0
        self._recalculate_mode()
        return None

    def _recalculate_mode(self):
        self.set_mode((int(self._toggle_pressed)) % self.number_of_modes())
    def update_master_mode(self):
        if self._master_mode:
            self._mixer.channel_strip(7).set_select_button(None) 
            self._session.scene(0).clip_slot(7).set_launch_button(None)
            self._mixer.master_strip().set_select_button(self._select_buttons[7]) 
            self._session.set_show_scene_button(self._clip_launch_buttons[7])
        else:
            self._mixer.master_strip().set_select_button(None) 
            self._session.set_show_scene_button(None)
            self._mixer.channel_strip(7).set_select_button(self._select_buttons[7])
            self._session.scene(0).clip_slot(7).set_launch_button(self._clip_launch_buttons[7])
            self._session.scene(0).clip_slot(7).set_triggered_to_play_value(0)               