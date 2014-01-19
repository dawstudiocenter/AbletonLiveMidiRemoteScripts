from _Framework.ControlElement import ControlElement
from consts import DISPLAY_FAST_DELAY, DISPLAY_LONG_DELAY, NUM_CHARS_PER_DISPLAY_LINE, NUM_CHARS_PER_DISPLAY_STRIP, CLEAR_LEFT_DISPLAY, CLEAR_RIGHT_DISPLAY, SYSEX_HEADER

class SLDisplay(ControlElement):
    ' Display ' 
    
    def __init__(self, sl_surface):
        self._sl = sl_surface
        self._left_strip_names = [ str() for x in range(8) ]
        self._left_strip_parameters = [ None for x in range(8) ]
        self._right_strip_names = [ str() for x in range(8) ]
        self._right_strip_parameters = [ None for x in range(8) ]
        self._empty_strip = [ None for x in range(8) ]

        self._update_display_count = 0
        self._last_send_row_id_messages = None
        self._block_messages = False
        self._hold_left = 0
        self._hold_right = 0
        self._hold_pot_light = -1
        self._pot_light_button = None
        self.refresh_state()
        
    def disconnect(self):
        self._send_clear_displays()

    #def hold_left_display(self, top_message='', bottom_message='', count=DISPLAY_FAST_DELAY):
        #self._hold_left = count
        #self._send_display_string(top_message, 1)
        #self._send_display_string(bottom_message, 3)
        ##self._block_left = False

    #def hold_right_display(self, top_message='', bottom_message='', count=DISPLAY_FAST_DELAY):
        #self._hold_right = count
        #self._send_display_string(top_message, 2)
        #self._send_display_string(bottom_message, 4)
        ##self._block_right = False
        
    def show_message_left(self, top_message='', bottom_message='', long_delay=False, pot_light=False):
        if self._hold_left > -1:
            if not long_delay:
                self._hold_left = DISPLAY_FAST_DELAY
            else:
                self._hold_left = DISPLAY_LONG_DELAY
                
        if pot_light and self._pot_light_button:
            self._pot_light_button.turn_on()
            #if self._hold_pot_light > -1:
            self._hold_pot_light = self._hold_left            
        else:
            self._hold_pot_light = 0

        self._send_display_string(top_message, 1)
        self._send_display_string(bottom_message, 3)
        
    def show_message_right(self, top_message='', bottom_message='', long_delay=False):
        #block_right_display(self, top_message='', bottom_message='', hold=False, long_delay=False):
        if self._hold_right > -1:
            if not long_delay:
                self._hold_right = DISPLAY_FAST_DELAY
            else:
                self._hold_right = DISPLAY_LONG_DELAY

        self._send_display_string(top_message, 2)
        self._send_display_string(bottom_message, 4)
        
    def set_block_left(self, block, delay=False):
        if block:
            self._hold_left = -1
        elif not delay:
            self._hold_left = 0
        else:
            self._hold_left = DISPLAY_FAST_DELAY
            
        if self._pot_light_button:
            self._hold_pot_light = self._hold_left
        
    def set_block_right(self, block, delay=False):
        if block:
            self._hold_right = -1
        elif not delay:
            self._hold_right = 0
        else:
            self._hold_right = DISPLAY_FAST_DELAY

    def setup_left_display(self, names, parameters=[ None for x in range(8) ]):
        assert ((len(names) == 8) or (len(names) == 1))
        assert (len(parameters) == 8)
        self._left_strip_names = names
        self._left_strip_parameters = parameters   
        
    def setup_right_display(self, names, parameters=[ None for x in range(8) ]):
        assert ((len(names) == 8) or (len(names) == 1))
        assert (len(parameters) == 8)
        self._right_strip_names = names
        self._right_strip_parameters = parameters
        
    def set_block_messages(self, block):
        assert isinstance(block, type(False))
        if block != self._block_messages:
            self._block_messages = block
        
    def update(self):
        if self._hold_left > 0:
            self._hold_left -= 1
                       
        if self._hold_right > 0:
            self._hold_right -= 1
        
        if self._hold_pot_light > 0:
            self._hold_pot_light -= 1 
            
        if self._pot_light_button and self._hold_pot_light == 0:
            self._pot_light_button.turn_off()
            self._hold_pot_light = -1 

        if (not self._block_messages):
            self._update_display_count += 1
            if (self._update_display_count >= 100):
                self._update_display_count = 0
                self.refresh_state()
            for row_id in (1,
             2,
             3,
             4):
                message_string = ''
                if ((row_id == 1) or (row_id == 2)):
                    if (row_id == 1):
                        strip_names = self._left_strip_names
                    else:
                        strip_names = self._right_strip_names
                    if (len(strip_names) == 8):
                        for s in strip_names:
                            message_string += self._adjust_strip_string(s)
    
                    else:
                        assert (len(strip_names) == 1)
                        message_string += strip_names[0]
                elif ((row_id == 3) or (row_id == 4)):
                    if (row_id == 3):
                        parameters = self._left_strip_parameters
                    else:
                        parameters = self._right_strip_parameters
                    assert (len(parameters) == 8)
                    for p in parameters:
                        if p:
                            message_string += self._adjust_strip_string(unicode(p))
                        else:
                            message_string += self._adjust_strip_string('')
    
                else:
                    assert False
                if ((row_id in (1,3) and not abs(self._hold_left)) or (row_id in (2,4) and not abs(self._hold_right))):
                    self._send_display_string(message_string, row_id, offset=0) 

    def refresh_state(self):
        self._last_send_row_id_messages = [None,
         [],
         [],
         [],
         []]       

    def _send_clear_displays(self):
        if (not self._block_messages):
            self.send_midi(CLEAR_LEFT_DISPLAY)
            self.send_midi(CLEAR_RIGHT_DISPLAY)        

    def _send_display_string(self, message, row_id, offset = 0):
        assert (row_id in [1,
         2,
         3,
         4])
        if (not self._block_messages):
            final_message = ((' ' * offset) + message)
            if (len(final_message) < NUM_CHARS_PER_DISPLAY_LINE):
                fill_up = (NUM_CHARS_PER_DISPLAY_LINE - len(final_message))
                final_message = (final_message + (' ' * fill_up))
            elif (len(final_message) >= NUM_CHARS_PER_DISPLAY_LINE):
                final_message = final_message[0:NUM_CHARS_PER_DISPLAY_LINE]
            final_offset = 0
            sysex_header = SYSEX_HEADER
            sysex_pos = (final_offset,
             row_id)
            sysex_text_command = (4,)
            sysex_text = tuple([ ord(c) for c in final_message ])
            sysex_close_up = (247,)
            full_sysex = ((((sysex_header + sysex_pos) + sysex_text_command) + sysex_text) + sysex_close_up)
            if (self._last_send_row_id_messages[row_id] != full_sysex):
                self._last_send_row_id_messages[row_id] = full_sysex
                #self._send_midi(full_sysex)  
                self._sl._send_midi(full_sysex)  
        
    def _adjust_strip_string(self, display_string, length=NUM_CHARS_PER_DISPLAY_STRIP):
        if (not display_string):
            return (' ' * length)
        
        #--------------------------- round dB values
        display_string.strip()
        if (display_string.endswith('.adg(*)') or display_string.endswith('.adv(*)')):
            display_string = display_string[:-7]
            display_string += ' (*)'
            display_string.strip()
        if (display_string.endswith('.adg') or display_string.endswith('.adv')):
            display_string = display_string[:-4]
            display_string.strip()
        if (display_string.endswith('(Automap)')):
            display_string = display_string[:-9]
            display_string.strip()
            display_string += '(AmP)'
        if ((display_string.endswith('dB') and (display_string.find('.') != -1))):
            display_string = display_string[:-2]
            display_string.strip()
            try:
                x = float(display_string)
            except ValueError:
                pass
            else:
                display_string = "%.1f" % x 
                if (len(display_string) > (length - 1)):
                    pass
                elif (len(display_string) < (length - 3)):
                    display_string += ' dB'    
                elif (len(display_string) < (length - 2)):
                    display_string += 'dB'                     
        #--------------------------- -inf dB values
        if display_string.endswith('-inf dB'):
            display_string = '-inf'
            #display_string = '-'
            #display_string = ' '
        #---------------------------
        if (len(display_string) > (length - 1)):
            for um in [' ',
             'i',
             'o',
             'u',
             'e',
             'a']:
                while ((len(display_string) > (length - 1)) and (display_string.rfind(um, 1) != -1)):
                    um_pos = display_string.rfind(um, 1)
                    display_string = (display_string[:um_pos] + display_string[(um_pos + 1):])
        else:
            display_string = display_string.center((length - 1))
        ret = u''
        for i in range((length - 1)):
            if ((ord(display_string[i]) > 127) or (ord(display_string[i]) < 0)):
                ret += ' '
            else:
                ret += display_string[i]
        ret += ' '
        assert (len(ret) == length)
        return ret
    
    #def _send_midi(self, midi_bytes, optimized = None):
        #sent_successfully = False
        ##if not self._suppress_send_midi:
        #sent_successfully = ControlSurface._send_midi(self, midi_bytes, optimized=optimized)
        #return sent_successfully