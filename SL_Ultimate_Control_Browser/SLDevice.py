import Live
from _Generic.Devices import *
from _Framework.DeviceComponent import DeviceComponent  
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from consts import BUTTON_HOLD_DELAY

class SLDevice(DeviceComponent):
    ' gdgdfgdfgdf '

    def __init__(self, mixer, display):
        self._mixer = mixer
        self._display = display
        self._update_callback = None
        self._lock_button_pressed = False
        self._lock_button_pressed_time = 0
        self._lock_button_blink = False
        self._was_locked = False
        self._device_string = ''
        #DeviceComponent.__init__(self)
        super(SLDevice, self).__init__()
        self._register_timer_callback(self._on_custom_timer)

    def disconnect(self):
        self._unregister_timer_callback(self._on_custom_timer)
        self._display = None
        #DeviceComponent.disconnect(self)
        super(SLDevice, self).disconnect()

    def _on_custom_timer(self):
        if self.is_enabled():
            if self._lock_button_blink:
                if self._lock_button != None:
                    self._lock_button.turn_on()
                self._lock_button_blink = False
            if self._lock_button_pressed:
                self._lock_button_pressed_time += 1
                if self._lock_button_pressed_time == BUTTON_HOLD_DELAY:
                    if self._device:
                        self._was_locked = self._locked_to_device
                        self._lock_callback()
                        self._lock_button.turn_off()
                        self._lock_button_blink = True
                            
    def set_parameter_controls(self, controls):
        #assert (controls != None)
        if (controls != None):
            assert isinstance(controls, tuple)
            if self._device != None and self._parameter_controls != None:
                for control in self._parameter_controls:
                    control.release_parameter()
            for control in controls:
                assert (control != None)
                assert isinstance(control, EncoderElement)
            self._parameter_controls = controls
        else:
            self._parameter_controls = None
        self.update()
        return None        

    def update(self):
        #if self._parameter_controls != None:
            #for control in self._parameter_controls:
                #control.release_parameter()
        if (self.is_enabled() and (self._device != None)):
            self._device_bank_registry.set_device_bank(self._device, self._bank_index)
            if self._parameter_controls != None:
                if self._bank_index < number_of_parameter_banks(self._device):
                    old_bank_name = self._bank_name
                    self._assign_parameters()
                    if self._bank_name != old_bank_name:
                        self._show_msg_callback(self._device.name + ' Bank: ' + self._bank_name)

            #self._device_bank_registry[self._device] = self._bank_index
            #if (self._parameter_controls != None):
                #old_bank_name = self._bank_name #added
                #self._assign_parameters()
                #if self._bank_name != old_bank_name: #added
                    #self._show_msg_callback(self._device.name + ' Bank: ' + self._bank_name) #added
            if self._bank_up_button != None and self._bank_down_button != None:
                can_bank_up = self._bank_index == None or self._number_of_parameter_banks() > self._bank_index + 1
                can_bank_down = self._bank_index == None or self._bank_index > 0
                self._bank_up_button.set_light(can_bank_up)
                self._bank_down_button.set_light(can_bank_down)                    
            #if ((self._bank_up_button != None) and (self._bank_down_button != None)):
                #if (self._number_of_parameter_banks()) > (self._bank_index + 1):
                    #self._bank_up_button.turn_on()
                #else:
                    #self._bank_up_button.turn_off()
                #if (self._bank_index > 0):
                    #self._bank_down_button.turn_on()
                #else:
                    #self._bank_down_button.turn_off()
            #if (self._bank_buttons != None):
                #for index in range(len(self._bank_buttons)):
                    #if (index == self._bank_index):
                        #self._bank_buttons[index].turn_on()
                    #else:
                        #self._bank_buttons[index].turn_off()
        else:
            if (self._on_off_button != None):
                self._on_off_button.turn_off()            
            if (self._bank_up_button != None):
                self._bank_up_button.turn_off()
            if (self._bank_down_button != None):
                self._bank_down_button.turn_off()
            if (self._bank_buttons != None):
                for button in self._bank_buttons:
                    button.turn_off()
            if (self._parameter_controls != None):
                for control in self._parameter_controls:
                    control.release_parameter()        
        if (self.is_enabled()):
            if (self._device != None):
                #self.on_enabled_changed() #update on\off status on track select
                self.set_device_values()
            else:
                self._display.setup_left_display((' No device selected',))
        if self._update_callback != None:
            self._update_callback() 

    def _on_off_value(self, value):
        if (self.is_enabled()):
            #DeviceComponent._on_off_value(self, value)
            super(SLDevice, self)._on_off_value(value)
            #self.show_device()
            self.show_device_parameters()
            
    def set_lock_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if self._lock_button != None:
            self._lock_button.remove_value_listener(self._lock_value)
            self._lock_button = None
        self._lock_button = button
        if self._lock_button != None:
            self._lock_button.add_value_listener(self._lock_value)
        self._lock_button_pressed = False
        self._lock_button_pressed_time = 0              
        self.update()
        return None
        
    def _lock_value(self, value):
        assert (self._lock_button != None)
        #assert (self._lock_callback != None)
        assert (value != None)
        assert isinstance(value, int)
        if (self.is_enabled() and self._lock_callback != None):
            if not self._lock_button.is_momentary() or value is not 0:
                self._lock_button_pressed = True
            else:
                self._lock_button_pressed = False
                self._lock_button_pressed_time = 0                
        return None

    def update_lock_button(self):
        if self._lock_button != None:
            if self._locked_to_device:
                self._lock_button.turn_on()
            else:
                self._lock_button.turn_off()    

    def set_lock_to_device(self, lock, device):
        if lock:
            self.set_device(device)
        self._locked_to_device = lock
        if self._was_locked and self._locked_to_device:
            self._was_locked = False
            self._lock_callback()
        if self.is_enabled():
            if self._update_callback != None:
                self._update_callback() 
            #self.show_device() 
            self.show_device_parameters()

    def set_device(self, device):
        #DeviceComponent.set_device(self, device)
        super(SLDevice, self).set_device(device)
        assert ((device == None) or isinstance(device, Live.Device.Device))   
        if self.is_enabled() and not self._locked_to_device:
            if self._update_callback != None:
                self._update_callback() 
            self.show_device()

    def _bank_up_value(self, value):
        #DeviceComponent._bank_up_value(self, value)
        super(SLDevice, self)._bank_up_value(value)
        if self.is_enabled():
            if ((not self._bank_up_button.is_momentary()) or (value is not 0)):
                self.show_device_parameters()

    def _bank_down_value(self, value):
        #DeviceComponent._bank_down_value(self, value)
        super(SLDevice, self)._bank_down_value(value)
        if self.is_enabled():
            if ((not self._bank_down_button.is_momentary()) or (value is not 0)):
                self.show_device_parameters()
                
    def _is_banking_enabled(self):
        return True
    
    def get_root_device(self):
        root_device = self._device
        parent = root_device.canonical_parent
        while isinstance(parent, Live.Device.Device) or isinstance(parent, Live.Chain.Chain):
            root_device = parent
            parent = root_device.canonical_parent
        return root_device
    
    def update_device_string(self):
        device_string = ' No device'
        if self._device != None:
            device_string = ' Device:'+chr(16)

            if self._locked_to_device:
                device_string += '[Locked] '
                
            if (str(self._on_off_parameter())=='off'):
                device_string += '[Bypass] '#' [OFF]'                

            #class_name = self._device.class_display_name
            #name = self._device.name
            
            root = self.get_root_device()
            #root_name = self.get_root_name()
            #device_string += root_name + ' -> '
            if root and root != self._device:
                device_string += root.name + ' '+chr(126)+' '
            
            #device_string += class_name
            #if class_name != name:
            device_string += self._device.name#device_string += ' (' + name +')'
            
            
                
            if self._is_banking_enabled():
                num_banks = self._number_of_parameter_banks()
                if num_banks > 1:
                    device_string += ' [Bank '+str(self._bank_index+1)+'/'+str(num_banks)+': '+self._bank_name+'] '
            
            #========================== TEST ==========================
            #if self._device.can_have_chains:
                #device_string += ' [CHAIN: '
                #if self._device.view.selected_chain:
                    #device_string += self._device.view.selected_chain.name
                #device_string += ']'
            #if self._device.can_have_drum_pads:
                #device_string += ' [DRUMPAD: '
                #if self._device.view.selected_drum_pad:
                    #device_string += self._device.view.selected_drum_pad.name
                #device_string += ']'
                
            #if isinstance(self._device.canonical_parent, Live.Track.Track):
                #device_string += " [TRACK]"
            #========================== TEST ==========================
            
        self._device_string = device_string
        
    def show_device_parameters(self):
        self.update_device_string()
        if self.is_enabled():
            device_string = ' No device'
            param_string = ''
            if self._device != None and self._parameter_controls != None:
                for index in range(len(self._parameter_controls)):
                    if (self._parameter_controls[index].mapped_parameter() != None):  
                        param_string += self._display._adjust_strip_string(str(self._parameter_controls[index].mapped_parameter().name))
                    else:
                        param_string += '         '
                        
            self._display.show_message_left(self._device_string, param_string)
        
    def show_device(self):
        self.update_device_string()
        if self.is_enabled():
            track_string = ''
            if not self._locked_to_device:
                track_string = self._mixer._selected_tracks_string
                #if self.application().view.is_view_visible('Detail/DeviceChain') and self._device:
                    #self.application().view.focus_view('Detail/DeviceChain')                
            self._display.show_message_left(self._device_string, track_string, True)
            
        
    def _assign_parameters(self):
        #DeviceComponent._assign_parameters(self)
        super(SLDevice, self)._assign_parameters()
        for index in range(len(self._parameter_controls)):
            if (self._parameter_controls[index].mapped_parameter() != None):
                if (self._parameter_controls[index].mapped_parameter().value_has_listener(self._on_value_changed)):
                    self._parameter_controls[index].mapped_parameter().remove_value_listener(self._on_value_changed)
                self._parameter_controls[index].mapped_parameter().add_value_listener(self._on_value_changed)

    def _on_value_changed(self):
        self.set_device_values()

    def set_device_values(self):
        if (self.is_enabled() and (self._device != None) and (self._parameter_controls != None)):
            param_names = [ None for x in range(8) ]
            param_values = [ None for x in range(8) ]
            for index in range(len(self._parameter_controls)):
                if (self._parameter_controls[index].mapped_parameter() != None):  
                    param_names[index] = self._parameter_controls[index].mapped_parameter().name
                    #param_values[index] = str(self._parameter_controls[index].mapped_parameter())
                    param_values[index] = unicode(self._parameter_controls[index].mapped_parameter())
            self._display.setup_left_display(param_names, param_values)

    def release_parameter(self):
        if (self.mapped_parameter().value_has_listener(self._on_value_changed) != None):
            self.mapped_parameter().remove_value_listener(self._on_value_changed)    

