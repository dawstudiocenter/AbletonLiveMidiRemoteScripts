import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from SL_Ultimate_Extra_Device_Browser.SLExtraDeviceControl import SLExtraDeviceControl
from SLBrowserControl import *
from config import BROWSER_ENABLE

class SLDeviceControl(ControlSurfaceComponent):
    ' fffffsffsfasfafasfs '

    def __init__(self, device, display):
        ControlSurfaceComponent.__init__(self)
        self._display = display
        self._main_device = device
        self._extra_device = None
        
        if BROWSER_ENABLE:
            self._browser_device = None
        
        self._main_device._update_callback = self.update
        
        self._prev_device_button = None
        self._next_device_button = None 
        
        self._update_timer_count = 0
        self._register_timer_callback(self._on_custom_timer)
        #self.song().add_appointed_device_listener(self._device_changed)
                
    def disconnect(self):
        self._unregister_timer_callback(self._on_custom_timer)
        #self.song().remove_appointed_device_listener(self._device_changed)
        self._main_device = None
        self._extra_device = None
        if BROWSER_ENABLE:
            self._browser_device.disconnect()
            self._browser_device = None
        if self._prev_device_button != None:
            self._prev_device_button.remove_value_listener(self._nav_value)
            self._prev_device_button = None
        if self._next_device_button != None:
            self._next_device_button.remove_value_listener(self._nav_value)
            self._next_device_button = None         
        ControlSurfaceComponent.disconnect(self)
        
    def _on_custom_timer(self):
        if self.is_enabled():
            if self._update_timer_count > 10:
                if not self._extra_device and SLExtraDeviceControl._device:
                    #self.log_message((' '+'init extradevice in devicecontrol'+' ').center(50,'='))
                    self._extra_device = SLExtraDeviceControl._device
                    self._extra_device._update_callback = self.update
                if BROWSER_ENABLE and not self._browser_device and SLBrowserControl._device:
                    #self.log_message((' '+'init browser in devidecontrol'+' ').center(50,'='))
                    self._browser_device = SLBrowserControl._device
                    self._browser_device._update_callback = self.update
                self._update_timer_count = 0
            self._update_timer_count += 1
            
    #def _device_changed(self):
        #self.update()
        #device = self.song().appointed_device
        #device_str = 'None'
        #if device:
            #device_str = device.name
        #self.log_message("  =\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=  "+device_str)
        
    def update(self):
        self.update_nav_buttons()
    
    def get_any_free_device(self):
        any_device = None
        if self._main_device != None and self._main_device.is_enabled() and not self._main_device._locked_to_device:
            any_device = self._main_device._device
        elif self._extra_device != None and self._extra_device.is_enabled() and not self._extra_device._locked_to_device:
            any_device = self._extra_device._device
        return any_device
    
    def is_any_unlocked_device(self):
        is_any = False
        if (self._main_device != None and self._main_device.is_enabled() and not self._main_device._locked_to_device) or (self._extra_device != None and self._extra_device.is_enabled() and not self._extra_device._locked_to_device):
            is_any = True
        return is_any
    
    def set_device_nav_buttons(self, prev_device_button, next_device_button): 
        assert ((prev_device_button == None) or isinstance(prev_device_button, ButtonElement))
        assert ((next_device_button == None) or isinstance(next_device_button, ButtonElement))
        identify_sender = True
        if self._prev_device_button != prev_device_button or self._next_device_button != next_device_button:
            if self._prev_device_button != None:
                self._prev_device_button.remove_value_listener(self._nav_value)
                self._prev_device_button.reset()
            self._prev_device_button = prev_device_button
            if self._prev_device_button != None:
                self._prev_device_button.add_value_listener(self._nav_value, identify_sender)
            if self._next_device_button != None:
                self._next_device_button.remove_value_listener(self._nav_value)
                self._next_device_button.reset()
            self._next_device_button = next_device_button
            if self._next_device_button != None:
                self._next_device_button.add_value_listener(self._nav_value, identify_sender)                
            self.update_nav_buttons()
            
    def _nav_value(self, value, sender):
        assert ((sender != None) and (sender in (self._prev_device_button, self._next_device_button)))
        if self.is_enabled():
            if (value != 0) or (not sender.is_momentary()):
                any_device = self.get_any_free_device()
                if any_device:
                    #devices = self.song().view.selected_track.devices
                    #modifier_pressed = True
                    #if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/DeviceChain'))):
                        #self.application().view.show_view('Detail')
                        #self.application().view.show_view('Detail/DeviceChain')
                    #direction = Live.Application.Application.View.NavDirection.left
                    #if (sender == self._next_device_button):
                        #direction = Live.Application.Application.View.NavDirection.right
                    #if devices:
                        #device_count = len(devices)
                        #if (direction == Live.Application.Application.View.NavDirection.right and any_device == devices[device_count-1] and not any_device.can_have_chains):
                            #pass
                        #else:
                            #self.application().view.scroll_view(direction, 'Detail/DeviceChain', (not modifier_pressed))
                    
                    #self._display.show_message_left("any_device")
                    
                    new_device = None
                    if (sender == self._next_device_button):
                        new_device = self.get_next_device(any_device)
                    else:
                        new_device = self.get_prev_device(any_device)
                        
                    if new_device:
                        self.song().view.select_device(new_device)
                    else:
                        parent = self.get_root_device(any_device)
                        #if parent != any_device:
                        self.song().view.select_device(parent)                        
                    
                    #if (sender == self._next_device_button):
                        #next_device = self.get_next_device(any_device)
                        #if next_device:
                            #self.song().view.select_device(next_device)
                            
                    #else: #PREV BUTTON
                        #prev_device = self.get_prev_device(any_device)
                        #if prev_device:
                            #self.song().view.select_device(prev_device)
                        #else:
                            #parent = self.get_root_device(any_device)
                            #if parent != any_device:
                                #self.song().view.select_device(parent)
                   
                elif self.is_any_unlocked_device(): 
                    self.song().view.selected_track.view.select_instrument()
                    #devices = self.song().view.selected_track.devices
                    #if devices:
                        #self.song().view.select_device(devices[0]) 
                    
                            
    def get_next_device(self, device):
        current_device = self.get_root_device(device)
        next_device = None
        devices = self.song().view.selected_track.devices
        if devices:
            device_count = len(devices)
            for index in range(device_count):
                if devices[index] == current_device:
                    if index+1 < device_count:
                        next_device = devices[index+1]
                    break
        return next_device
    
    def get_prev_device(self, device):
        current_device = self.get_root_device(device)
        prev_device = None
        devices = self.song().view.selected_track.devices
        if devices:
            device_count = len(devices)
            for index in range(device_count):
                if devices[index] == current_device:
                    if index > 0:
                        prev_device = devices[index-1]
                    break
        return prev_device    
        
    def get_root_device(self, device):
        root_device = device
        parent = root_device.canonical_parent
        #test_str = ' -> '+parent.name 
        while isinstance(parent, Live.Device.Device) or isinstance(parent, Live.Chain.Chain):
            root_device = parent
            parent = root_device.canonical_parent
            #test_str = ' -> '+parent.name 
        #self._display.show_message_left(test_str)
        return root_device
    
    def get_track(self, device):
        
        return None
    
    def update_nav_buttons(self):
        if self.is_enabled() and self._prev_device_button != None and self._next_device_button != None:
            devices = self.song().view.selected_track.devices
            any_device = self.get_any_free_device()
            if devices and any_device:
                
                #device_count = len(devices)
                #if any_device == devices[device_count-1]:# and not any_device.can_have_chains: #last device
                    #self._next_device_button.turn_off()
                #else:
                    #self._next_device_button.turn_on()
                #if any_device != devices[0]:
                    #self._prev_device_button.turn_on()
                #else: #first device
                    #self._prev_device_button.turn_off()
                
                next_device = self.get_next_device(any_device)
                prev_device = self.get_prev_device(any_device)
                if next_device:
                    self._next_device_button.turn_on() 
                else:
                    self._next_device_button.turn_off()
                if prev_device:
                    self._prev_device_button.turn_on()
                else:
                    self._prev_device_button.turn_off()
                    
            else: #no device or locked
                self._prev_device_button.turn_off()
                self._next_device_button.turn_off()
