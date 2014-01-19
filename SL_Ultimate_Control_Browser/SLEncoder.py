from _Framework.EncoderElement import EncoderElement 
from _Framework.ButtonElement import ButtonElement 
#from _Framework.NotifyingControlElement import NotifyingControlElement 

RING_OFF_VALUE = 0
RING_SIN_VALUE = 64 #1
RING_VOL_VALUE = 0  #2
RING_PAN_VALUE = 32 #3

class SLEncoder(EncoderElement):
    ' Clgfgdfgdfgng '

    def __init__(self, msg_type, channel, identifier, map_mode):
        self._support_mkII = False
        EncoderElement.__init__(self, msg_type, channel, identifier, map_mode)
        self._ring_mode_button = None
        self._led_ring_encoder = None
        self.set_needs_takeover(False)


    def set_ring_mode_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._ring_mode_button != None):
            force_send = True
            self._ring_mode_button.send_value(RING_OFF_VALUE, force_send)
        self._ring_mode_button = button
        self._update_ring_mode()

    def set_led_ring_feedback(self, encoder):
        self._led_ring_encoder = encoder

    def update_ring(self):
        if self._support_mkII:
            force_send = True
            param = self._parameter_to_map_to
            #p_range = (param.max - param.min)
            #value = ((((param.value - param.min) / p_range) * 10) + 1)
            step = (param.max - param.min)/10
            value = ((param.value+(step/2))-param.min)/step + 1        
            self._led_ring_encoder.send_value(int(value), force_send)
        
    def connect_to(self, parameter):
        if ((parameter != self._parameter_to_map_to) and (not self.is_mapped_manually())):
            force_send = True
            #self._ring_mode_button.send_value(RING_OFF_VALUE, force_send)
        EncoderElement.connect_to(self, parameter)
        if (self._parameter_to_map_to.value_has_listener(self.update_ring)):
            self._parameter_to_map_to.remove_value_listener(self.update_ring)
        self._parameter_to_map_to.add_value_listener(self.update_ring)

    def release_parameter(self):
        if (self._parameter_to_map_to != None):
            self._parameter_to_map_to.remove_value_listener(self.update_ring)        
        EncoderElement.release_parameter(self)
        self._update_ring_mode()

    def install_connections(self, install_translation_callback, install_mapping_callback, install_forwarding_callback):
        EncoderElement.install_connections(self, install_translation_callback, install_mapping_callback, install_forwarding_callback)
        if not self._is_mapped and self.value_listener_count() == 0:
            self._is_being_forwarded = install_forwarding_callback(self)
        self._update_ring_mode()
        #def install_connections(self):
            #EncoderElement.install_connections(self)
            #if ((not self._is_mapped) and (len(self._value_notifications) == 0)):
                #self._is_being_forwarded = self._install_forwarding(self)
            #self._update_ring_mode()

    def is_mapped_manually(self):
        return ((not self._is_mapped) and (not self._is_being_forwarded))


    def _update_ring_mode(self):
        if self._support_mkII and self._ring_mode_button != None and self._led_ring_encoder != None:
            force_send = True
            if self.is_mapped_manually():
                self._ring_mode_button.send_value(RING_SIN_VALUE, force_send)
            elif (self._parameter_to_map_to != None):
                param = self._parameter_to_map_to
                #p_range = (param.max - param.min)
                #value = ((((param.value - param.min) / p_range) * 10) + 1)
                step = (param.max - param.min)/10
                value = ((param.value+(step/2))-param.min)/step + 1                  
                self.send_value(int(value), force_send)
                if (self._parameter_to_map_to.min == (-1 * self._parameter_to_map_to.max)):
                    self._ring_mode_button.send_value(RING_PAN_VALUE, force_send)
                elif self._parameter_to_map_to.is_quantized:
                    self._ring_mode_button.send_value(RING_SIN_VALUE, force_send)
                else:
                    self._ring_mode_button.send_value(RING_VOL_VALUE, force_send)
                self._led_ring_encoder.send_value(int(value), force_send)
            else:
                self._led_ring_encoder.send_value(RING_OFF_VALUE, force_send)
                self._ring_mode_button.send_value(RING_OFF_VALUE, force_send)

