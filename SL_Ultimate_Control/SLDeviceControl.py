import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from SL_Ultimate_Extra_Device.SLExtraDeviceControl import SLExtraDeviceControl

class SLDeviceControl(ControlSurfaceComponent):
    ' fffffsffsfasfafasfs '

    def __init__(self, device, display,logger):
        ControlSurfaceComponent.__init__(self)
        self._display = display
        self._main_device = device
        self._extra_device = None
        self.log = logger
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
                    self._extra_device = SLExtraDeviceControl._device
                    self._extra_device._update_callback = self.update
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
                    
                    #new_device = None
                    if (sender == self._next_device_button):
                        #new_device = self.get_next_device(any_device)
                        self.next_device_button()
                    else:
                        #new_device = self.get_prev_device(any_device)
                        self.prev_device_button()
                        
                    # if new_device:
                    #     self.song().view.select_device(new_device)
                    # else:
                    #     parent = self.get_root_device(any_device)
                    #     #if parent != any_device:
                    #     self.song().view.select_device(parent)
                    
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
                    
    def prev_device_button(self):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.left)

    def next_device_button(self):
        self._scroll_device_view(Live.Application.Application.View.NavDirection.right)

    def _scroll_device_view(self, direction):
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')
        self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    def get_device_index(self, device, devices):
        index = 0
        for d in devices:
            if d == device:
                return index
            index = index + 1
        return -1
        
    def get_device_relative_recursive(self, selected_device, delta):
        container = selected_device.canonical_parent # either track or chain
        if container:
            len_devices = len(container.devices)
            index = self.get_device_index(selected_device, container.devices) + delta
        
            if not type(container) == type(Live.Track.Track):
                # as we are not inside a Track, we must be inside a Rack
                if index < 0:
                    # if first device is selected and we move left, try to move up a device_container and select the containing device
                    return self.get_device_relative_recursive(container.canonical_parent, index+1)
                elif index >= len_devices:
                    # if last device is selected and we move right, try to move up a device_container and select next device
                    #return self.get_device_relative_recursive(container.canonical_parent, index-len_devices+1)
                    # if last device is selected and we move right, try to move up a device_container and select the containing device
                    return self.get_device_relative_recursive(container.canonical_parent, index-len_devices)
            
            # we cannot move further out => stay inside the index-boundary of available devices
            index = max(0, min(len_devices-1, index))
            
            return container.devices[index]
        else:
            return None
    
    def scroll_devices(self, value):
        # relative navigation
        device = None
        relative_parent = self._main_device.song().view.selected_track.view.selected_device
        #self.log("  =\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=  "+relative_parent)
        if relative_parent:
            device = self.get_device_relative_recursive(relative_parent, value)
        return device

    def get_next_device(self, device):
        # current_device = self.get_root_device(device)
        next_device = None
        # devices = self.song().view.selected_track.devices
        # if devices:
        #     device_count = len(devices)
        #     for index in range(device_count):
        #         if devices[index] == current_device:
        #             if index+1 < device_count:
        #                 next_device = devices[index+1]
        #             break
        return next_device
    
    def get_prev_device(self, device):

        # current_device = self.get_root_device(device)
        prev_device = None
        # devices = self.song().view.selected_track.devices
        # if devices:
        #     device_count = len(devices)
        #     for index in range(device_count):
        #         if devices[index] == current_device:
        #             if index > 0:
        #                 prev_device = devices[index-1]
        #             break
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
                
                device_count = len(devices)
                if any_device == devices[device_count-1] and not any_device.can_have_chains: #last device
                    self._next_device_button.turn_off()
                else:
                    self._next_device_button.turn_on()
                if any_device != devices[0]:
                    self._prev_device_button.turn_on()
                else: #first device
                    self._prev_device_button.turn_off()
                
                # next_device = self.get_next_device(any_device)
                # prev_device = self.get_prev_device(any_device)
                # if next_device:
                #     self._next_device_button.turn_on() 
                # else:
                #     self._next_device_button.turn_off()
                # if prev_device:
                #     self._prev_device_button.turn_on()
                # else:
                #     self._prev_device_button.turn_off()
                    
            else: #no device or locked
                self._prev_device_button.turn_off()
                self._next_device_button.turn_off()
