import Live 
from consts import *
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector 
from _Framework.ButtonElement import ButtonElement 

from SL_Ultimate_Extra_Device_Browser.SLExtraDeviceControl import *
from SLBrowserControl import *
from SLBrowser import *

from config import DEFAULT_POT_MODE, SMART_VIEW, BROWSER_ENABLE

class SLPotModeSelector(ChannelTranslationSelector):
    ' fdfs '

    def debug(self,msg):
        return self._parent.log(msg)
    
    def __init__(self, mixer, pots, parent=None):
        if BROWSER_ENABLE:
            assert DEFAULT_POT_MODE < 17
        else:
            assert DEFAULT_POT_MODE < 9
        
        ChannelTranslationSelector.__init__(self)
        self._master_mode = False
        self._mode_names = [' TRACK   ','  PAN    ',' SEND A  ',' SEND B  ',' SEND C  ',' SEND D  ',' SEND E  ',' SEND F  ',' DEVICE  ',' BROWSR  ']
        self._mixer = mixer
        self._pots = pots
        self._parent = parent
        #self._extra_device = None
                 
        self.set_mode(DEFAULT_POT_MODE)
        #self.set_mode(8)

    def disconnect(self):
        ChannelTranslationSelector.disconnect(self)
        self._mixer = None
        self._pots = None

    def set_mode_buttons(self, buttons):
        assert isinstance(buttons, (tuple, type(None)))
        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)
        self._modes_buttons = []
        if (buttons != None):
            index = 0
            if len(buttons) == 9 :
                #self.log_message('hello')
                pass
            elif len(buttons) == 17 :
                #self.log_message('hello')
                pass
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
        if BROWSER_ENABLE:
            return 17
        else:
            return 9

    def update(self):
        log_message((' '+'Update'+' ').center(50,'='))
        #ChannelTranslationSelector.update(self)
        if self.is_enabled():
            self._mixer._pot_mode_index = self._mode_index
            #self._mixer._reassign_tracks()
            
            for index in range(len(self._modes_buttons)):
                if (index == self._mode_index):
                    self._modes_buttons[index].turn_on()
                else:
                    self._modes_buttons[index].turn_off()  
            
            #browser device control
            if BROWSER_ENABLE and not self._mixer._browser_device and SLBrowserControl._device:
                self._mixer._browser_device = SLBrowserControl._device
                if self._mixer._display != None :
                    SLBrowser._display = self._mixer._display
            if BROWSER_ENABLE and self._mixer._browser_device:
                self._mixer._browser_device.set_enabled(0)
                self._mixer._browser_device.set_parameter_controls(None)  
                self._mixer._browser_device.set_mode_selector(None)
            #extra device control
            
            #if SLExtraDeviceControl._device:
            if not self._mixer._extra_device and SLExtraDeviceControl._device:
                self._mixer._extra_device = SLExtraDeviceControl._device
                SLExtraDevice._display = self._mixer._display
                SLExtraDevice._main_device = self._mixer._device
            if self._mixer._extra_device:
                self._mixer._extra_device.set_enabled(0)
                self._mixer._extra_device.set_parameter_controls(None)  
            #selected strip
            selected_strip = self._mixer.selected_strip()
            selected_strip.set_pan_control_2(None)
            selected_strip.set_volume_control_2(None)
            selected_strip.set_send_controls_2((None, None, None, None, None, None))  
            selected_strip.set_cue_volume_control_2(None)
            #channel strips
            for index in range(8):
                strip = self._mixer.channel_strip(index)
                pot = self._pots[index]
                strip.set_pan_control_2(None)
                strip.set_volume_control_2(None)
                strip.set_send_controls_2((None, None, None, None, None, None))
                strip.set_cue_volume_control_2(None)
                pot.release_parameter()
            #master strip
            master_strip = self._mixer.master_strip()
            master_strip.set_pan_control_2(None)
            master_strip.set_volume_control_2(None)
            master_strip.set_send_controls_2((None, None, None, None, None, None))
            master_strip.set_cue_volume_control_2(None)
            self._pots[7].release_parameter()
            #self._mixer.set_tempo_control(None, None, None)
            #self.debug('Pot Mode : %d' % self._mode_index)
            if BROWSER_ENABLE and (self._mode_index == 13): #BROWSER DEVICE MODE                
                if self._mixer._browser_device:
                    #if not self._mixer._browser_device._device:
                        #self.song().view.selected_track.view.select_instrument()
                    self._mixer._browser_device.set_browser_mode(4)
                    self._mixer._browser_device.set_enabled(1)
                    self._mixer._browser_device.set_parameter_controls(tuple(self._pots))
                    self._mixer._browser_device.set_mode_selector(self)
            elif BROWSER_ENABLE and (self._mode_index == 12): #BROWSER DEVICE MODE                
                if self._mixer._browser_device:
                    #if not self._mixer._browser_device._device:
                        #self.song().view.selected_track.view.select_instrument()
                    self._mixer._browser_device.set_browser_mode(3)
                    self._mixer._browser_device.set_enabled(1)
                    self._mixer._browser_device.set_parameter_controls(tuple(self._pots))
                    self._mixer._browser_device.set_mode_selector(self)
            elif BROWSER_ENABLE and (self._mode_index == 11): #BROWSER DEVICE MODE                
                if self._mixer._browser_device:
                    #if not self._mixer._browser_device._device:
                        #self.song().view.selected_track.view.select_instrument()
                    self._mixer._browser_device.set_browser_mode(2)
                    self._mixer._browser_device.set_enabled(1)
                    self._mixer._browser_device.set_parameter_controls(tuple(self._pots))
                    self._mixer._browser_device.set_mode_selector(self)
            elif BROWSER_ENABLE and (self._mode_index == 10): #BROWSER DEVICE MODE                
                if self._mixer._browser_device:
                    #if not self._mixer._browser_device._device:
                        #self.song().view.selected_track.view.select_instrument()     
                    self._mixer._browser_device.set_browser_mode(1)
                    self._mixer._browser_device.set_enabled(1)
                    self._mixer._browser_device.set_parameter_controls(tuple(self._pots))
                    self._mixer._browser_device.set_mode_selector(self)
            elif BROWSER_ENABLE and (self._mode_index == 9): #BROWSER DEVICE MODE                
                if self._mixer._browser_device:
                    #if not self._mixer._browser_device._device:
                        #self.song().view.selected_track.view.select_instrument()     
                    self._mixer._browser_device.set_browser_mode(0)
                    self._mixer._browser_device.set_enabled(1)
                    self._mixer._browser_device.set_parameter_controls(tuple(self._pots))
                    self._mixer._browser_device.set_mode_selector(self)
            elif (self._mode_index == 8): #EXTRA DEVICE MODE
                if self._mixer._extra_device:
                    if not self._mixer._extra_device._device:
                        self.song().view.selected_track.view.select_instrument()                    
                    self._mixer._extra_device.set_enabled(1)
                    self._mixer._extra_device.set_parameter_controls(tuple(self._pots))
                
            elif (self._mode_index == 0): #TRACK MODE
                
                self._mixer._selected_strip.set_volume_control_2(self._pots[0])
                self._mixer._selected_strip.set_pan_control_2(self._pots[1])
                
                if self._mixer.selected_strip()._track != self._mixer.master_strip()._track: #NOT MASTER TRACK
                    snd_ctr = [self._pots[index+2] for index in range(6)]
                    self._mixer._selected_strip.set_send_controls_2(tuple(snd_ctr)) 
                else: # MASTER TRACK
                    #self._mixer.set_tempo_control(self._pots[0], self._pots[1], self._pots[2])
                    self._mixer._selected_strip.set_cue_volume_control_2(self._pots[3])                

            elif (self._mode_index == 1): #PAN MODE   
                for index in range(7):
                    strip = self._mixer.channel_strip(index)
                    strip.set_pan_control_2(self._pots[index])
                #self._mixer.master_strip().set_pan_control_2(self._pots[7])                

            elif (self._mode_index < 8): #SENDS A-F MODE 
                for index in range(7):
                    strip = self._mixer.channel_strip(index)
                    send_controls = [None, None, None, None, None, None, None]
                    send_controls[self._mode_index-2] = self._pots[index]
                    strip.set_send_controls_2(tuple(send_controls))
            self.update_master_mode()

    def update_master_mode(self):
        strip = self._mixer.channel_strip(7)
        master_strip = self._mixer.master_strip()
        pot = self._pots[7]
        if (self._mode_index == 13): #BROWSER DEVICE MODE
            pass
        elif (self._mode_index == 12): #BROWSER DEVICE MODE
            pass
        elif (self._mode_index == 11): #BROWSER DEVICE MODE
            pass
        elif (self._mode_index == 10): #BROWSER DEVICE MODE
            pass
        elif (self._mode_index == 9): #BROWSER DEVICE MODE
            pass
        elif (self._mode_index == 8): #EXTRA DEVICE MODE
            pass        
        elif (self._mode_index == 0): #TRACK MODE            
            pass      
        
        elif (self._mode_index == 1): #PAN MODE            
            pot.release_parameter()
            if self._master_mode:
                strip.set_pan_control_2(None)
                master_strip.set_pan_control_2(pot)
            else:
                master_strip.set_pan_control_2(None)
                strip.set_pan_control_2(pot)
                
        elif (self._mode_index < 8): #SENDS A-F MODE             
            pot.release_parameter()
            send_controls = [None, None, None, None, None, None, None]
            if self._master_mode:
                pass
            else:
                send_controls[self._mode_index-2] = pot
            strip.set_send_controls_2(tuple(send_controls))              

    def _mode_value(self, value, sender):
        ChannelTranslationSelector._mode_value(self, value, sender)
        if ((value != 0) or (not sender.is_momentary())):
            if (self._mode_index != 8) and (self._mode_index < 8):                
                self.show_modes()
            else:
                #self._mixer._extra_device.show_device()
                if (self._mode_index == 8):    
                    self._mixer._extra_device.show_device_parameters()
                elif BROWSER_ENABLE and (self._mode_index == 9): #ABLETON LIBRARY BROWSER
                    #self.debug('mode value')
                    self._mixer._browser_device.show_device_parameters()
                elif BROWSER_ENABLE and (self._mode_index == 10): #FAVORITES BROWSER
                    #self.debug('mode value')
                    self._mixer._browser_device.show_device_parameters()
                elif BROWSER_ENABLE and (self._mode_index == 11): #RECENT BROWSER
                    #self.debug('mode value')
                    self._mixer._browser_device.show_device_parameters()
                elif BROWSER_ENABLE and (self._mode_index == 12): #HOTSWAP MODE BROWSER
                    #self.debug('mode value')
                    self._mixer._browser_device.show_device_parameters()
                elif BROWSER_ENABLE and (self._mode_index == 13): #CUSTOM BROWSER
                    #self.debug('mode value')
                    self._mixer._browser_device.show_device_parameters()
            #if (SMART_VIEW) and (self._mode_index == 8): #device mode
                #if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/DeviceChain'))):
                    #self.application().view.show_view('Detail')
                    #self.application().view.show_view('Detail/DeviceChain')
            
    def show_modes(self):
        mode_names = ''
        for index in range(9):
            if self._mode_index != index:
                mode_names += self._mode_names[index]
            else:
                if index != 0:
                    mode_names = mode_names[:-1] + '['
                mode_names += self._mode_names[index][:-1]+']'

        self._mixer._display.show_message_left(' Pot Mode: '+self._mode_names[self._mode_index].strip(), mode_names)

    def on_selected_track_changed(self):
        #if (self._mode_index == 0): #track mode
        self.update() 
        return None
    
    #def on_track_list_changed(self):
        #self.update()
        #return None