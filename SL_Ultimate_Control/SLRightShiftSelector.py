#import Live
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from config import P2_INVERT_SHIFT_MODE

class SLRightShiftSelector(ModeSelectorComponent):
    __doc__ = ' gdfg '
    
    def __init__(self, mixer, session, transport, master_mode, slider_row_select_button, button_modes, first_row_select_button):
        ModeSelectorComponent.__init__(self)
        self._toggle_pressed = False
        self._mixer = mixer
        self._session = session
        self._transport = transport
        self._master_mode = master_mode
        self._slider_row_select_button = slider_row_select_button
        self._button_modes = button_modes
        self._first_row_select_button = first_row_select_button
        
        self._master_mode.set_master_mode_button(self._slider_row_select_button)
        self._button_modes.set_mode_toggle(self._first_row_select_button)
        
    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._mixer = None
        self._session = None
        self._master_mode = None
        self._slider_row_select_button = None
        self._button_modes = None
        self._first_row_select_button = None        
        return None

    def set_mode_toggle(self, button):
        ModeSelectorComponent.set_mode_toggle(self, button)
        self.set_mode(0)

    def number_of_modes(self):
        return 2

    def update(self):
        if self.is_enabled():
            if (self._mode_index == 0):
                #UNSHIFTED
                self._master_mode.set_master_mode_button(None)
                self._button_modes.set_mode_toggle(None)
                
                self._transport.set_main_view_button(self._slider_row_select_button)
                self._transport.set_detail_view_button(self._first_row_select_button)
                
                self._session.set_track_banking_increment(1 + ((7-int(self._master_mode._master_mode))*int(not P2_INVERT_SHIFT_MODE)))
                
                self._mixer._shift_pressed = False
                self._mode_toggle.turn_off()
                self._mixer._display.set_block_right(False)
            elif (self._mode_index == 1):
                #SHIFTED
                self._transport.set_main_view_button(None)
                self._transport.set_detail_view_button(None)
                
                self._master_mode.set_master_mode_button(self._slider_row_select_button)
                self._button_modes.set_mode_toggle(self._first_row_select_button)

                self._session.set_track_banking_increment(1 + ((7-int(self._master_mode._master_mode))*int(P2_INVERT_SHIFT_MODE)))
                
                self._mixer._shift_pressed = True
                self._mode_toggle.turn_on()
                self._mixer._display.set_block_right(True)
                #self._button_modes.show_modes()
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
