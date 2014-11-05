import Live
import sys
from _Generic.Devices import *
from _Framework.DeviceComponent import DeviceComponent  
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from consts import BUTTON_HOLD_DELAY, NUM_CHARS_PER_DISPLAY_LINE
from config import MIDI1_TRACK_COLOR,AUDIO_TRACK_COLOR,RECENT_PRESETS_FILE,FAVORITE_PRESETS_FILE,BACKUP_SETTINGS_FILE,AUTO_REFRESH_FOLDER_PREFIX
from SLPresetMenus import SLLiveCoreLibMenu,SLRecentLivePresetsMenu,SLFavoriteLivePresetsMenu,SLLiveHotswapPresetsMenu
from SLGlobalMenus import SLGlobalMenu
from SLLiveActions import BrowserActions,TrackActions
from SLCustomMapping import SLPadMapping

#NUM_CONTROLS_PER_ROW = 4

class SLBrowser(DeviceComponent):
    ' gdgdfgdfgdf '
    
    _display = None
    _main_device = None
    
    def debug(self,msg):
        #s = msg.encode('utf-8')
        return self.__parent.log_message(msg)
        
    def __init__(self, parent):
        self._update_callback = None
        self._device_string = ' Browser '
        self.__parent = parent
        self._mode_selector = None
        self._action_controls = None
        self._is_last_nav = False
        self._active_browser = None
        self._mapping = SLPadMapping(self)    
        DeviceComponent.__init__(self)
        self._init_browser()
        #self._register_timer_callback(self._on_custom_timer)
        self._init_task = None
        self._init_done = False
        #self._load_favorites()
        #self._load_recent()
        #self._load_last_mappings()
        
    def background_startup(self):        
        self.debug("Browser Creation Task currently Running")        
        self._load_browser()               
        self._load_favorites()
        self._load_recent()
        self._load_last_mappings()        
        self._active_browser = self._select_browser()
        self.debug("Browser Creation Task End")
        self._init_done = True   
        
    def check_browser_init(self):
        if not self._init_done:
            self._display.show_message_left(' Loading Browser, Please Wait...', '', False, False)
            self._init_task.resume()
            self.debug("init not started,now running")
            return False
        else:
            #self.debug("init already done")
            self._init_task.kill()
            return True        
        
    def disconnect(self):
        self._save_favorites()
        self._save_recent()
        self._autosave_mappings()
        
        #self._unregister_timer_callback(self._on_custom_timer)
        DeviceComponent.disconnect(self)
    
    def _on_custom_timer(self):
        if self.is_enabled():
            pass 
    
    def set_mode_selector(self,modeselector):
        self._mode_selector = modeselector
    
    def force_mode_selector(self,value):
        self._mode_selector.set_mode(value)
        
    def set_browser_mode(self, mode):
        self._browser_mode = mode%5
        self._active_browser = self._select_browser()
        if not self._init_done:
            return
            
        
 
        self.debug('Entering in Browser Mode : %d' % self._browser_mode)
        if self._browser_mode == 3: #HOTSWAP BROWSER
            self._hotswap_mode = not(self._hotswap_mode)
            if self._hotswap_mode:
                if self.application().view.browse_mode:
                    self.application().view.toggle_browse()
            self.application().view.toggle_browse()
            self.show_device_values()
        else:
            if self._hotswap_mode:
                if self.application().view.browse_mode:
                    self.application().view.toggle_browse()
                self._hotswap_mode = not(self._hotswap_mode)

            
    def set_parameter_controls(self, controls):
        #assert (controls == None) or isinstance(controls, tuple)
        if controls != None:
            if self._parameter_controls != None:
                for control in self._parameter_controls:
                    control.release_parameter()                
            self._parameter_controls = controls
            self._assign_parameters()
        else:
            if self._parameter_controls != None:
                for control in self._parameter_controls:
                    control.release_parameter()          
            self._unassign_parameters()
            self._parameter_controls = controls
        self.update()
        return None  
           
    def set_action_controls(self, controls):
        #assert (controls == None) or isinstance(controls, tuple)
        if controls != None:
            if self._action_controls != None:
                for control in self._action_controls:
                    control.release_parameter()
            self._action_controls = controls
            self._assign_actions()
        else:
            if self._action_controls != None:
                for control in self._action_controls:
                    control.release_parameter()            
            self._unassign_actions()
            self._action_controls = controls
        self.update()
        return None  
 
    def _assign(self,button,action):
        if (button.value_has_listener(action)):
            button.remove_value_listener(action)
        button.add_value_listener(action)        
    def _unassign(self,button,action):        
        if (button.value_has_listener(action)):
            button.remove_value_listener(action)
                
    def _assign_actions(self): 
        actions = (
            self._on_action0_changed,
            self._on_action1_changed,
            self._on_action2_changed,
            self._on_action3_changed,
            self._on_action4_changed,
            self._on_action5_changed,
            self._on_action6_changed,
            self._on_action7_changed
            )
        if (self._action_controls != None):
            for idx in range(8):
                self._assign(self._action_controls[idx],actions[idx])

    def _unassign_actions(self): 
        actions = (
            self._on_action0_changed,
            self._on_action1_changed,
            self._on_action2_changed,
            self._on_action3_changed,
            self._on_action4_changed,
            self._on_action5_changed,
            self._on_action6_changed,
            self._on_action7_changed
            )
        if (self._action_controls != None):
            for idx in range(8):
                self._unassign(self._action_controls[idx],actions[idx])        
            
    def _assign_parameters(self):         
        actions = (
            self._on_param0_changed,
            self._on_param1_changed,
            self._on_param2_changed,
            self._on_param3_changed,
            self._on_param4_changed,
            self._on_param5_changed,
            self._on_param6_changed,
            self._on_param7_changed
            )
        if (self._parameter_controls != None):
            for idx in range(8):
                self._assign(self._parameter_controls[idx],actions[idx])

    def _unassign_parameters(self):
        actions = (
            self._on_param0_changed,
            self._on_param1_changed,
            self._on_param2_changed,
            self._on_param3_changed,
            self._on_param4_changed,
            self._on_param5_changed,
            self._on_param6_changed,
            self._on_param7_changed
            )
        if (self._parameter_controls != None):
            for idx in range(8):
                self._unassign(self._parameter_controls[idx],actions[idx])


    def _on_param0_changed(self,value):
        self.set_device_values(0,value)

    def _on_param1_changed(self,value):
        self.set_device_values(1,value)
 
    def _on_param2_changed(self,value):
        self.set_device_values(2,value)

    def _on_param3_changed(self,value):
        self.set_device_values(3,value)

    def _on_param4_changed(self,value):
        self.set_device_values(4,value)

    def _on_param5_changed(self,value):
        self.set_device_values(5,value)
        bank = (value * 6) / 127        
        self._mapping.activate_bank(bank)
        disp_string = ''
        strings = self._mapping.get_bank_action_names(bank)
        for val in range(len(strings)):
            if val == 0:
                disp_string += SLBrowser._display._adjust_strip_string('MAIN',length=NUM_CHARS_PER_DISPLAY_LINE/8)
                disp_string += SLBrowser._display._adjust_strip_string('ALT',length=NUM_CHARS_PER_DISPLAY_LINE/8)
            else:
                disp_string += SLBrowser._display._adjust_strip_string(strings[val],length=NUM_CHARS_PER_DISPLAY_LINE/8)
        self._display.show_message_left(strings[0]+':',disp_string, True, False)
    def _on_param6_changed(self,value):
        pass
        
    def _on_param7_changed(self,value):
        pass

    def set_device_values(self,id,value):
        if (self.is_enabled() and (self._parameter_controls != None)):
            
            if not self.check_browser_init():
                return
            self.param_values[id] = value
            if id < 4: # store last selected browsing category
                self._is_last_nav=True
                self._last_category_id=id
            else:
                self._is_last_nav=False
                if id == 4:
                    self._is_last_nav=True
            # elif id == 7 and self._apha_mode : #if tune after enter dico mode then enter fine tune dico mode
                # self._alpha_fine_tune_mode = True
            # elif id == 6: # only change zoom factor
                # self._view_zoom_factor = NUM_CONTROLS_PER_ROW - ((value * (NUM_CONTROLS_PER_ROW-1))/127)
                # self._previous_view_zoom_factor = self._view_zoom_factor
            # else: #leave dico fine tune mode
                # self._alpha_fine_tune_mode = False
                # if id == 5: #enter recent list browse mode, automatically switch to 1 column view mode
                    # self._last_category_id=id
                    # if not self._recent_list_mode:
                        # self._previous_view_zoom_factor = self._view_zoom_factor
                        # self._view_zoom_factor = 1
                        # self._recent_list_mode = True                    
                # else: #leave recent list browsing mode if it was active
                    # if self._recent_list_mode:
                        # self._view_zoom_factor = self._previous_view_zoom_factor
                        # self._recent_list_mode = False
                # if id == 4: #enter dico mode
                    # self._apha_mode = True
                # else:
                    # self._apha_mode = False

            
    def _on_action0_changed(self,value):
        if self._active_menu != None:
            self._on_enter(self._active_menu)            
  
    def _on_action1_changed(self,value):
        if self._active_menu != None:
            self._on_alternate(self._active_menu)  
    

                    
    def _on_action2_changed(self,value):
        self._mapping.call(1)        
    def _on_action3_changed(self,value):
        self._mapping.call(2)                
    def _on_action4_changed(self,value):
        self._mapping.call(3)        
    def _on_action5_changed(self,value):
        self._mapping.call(4)        
    def _on_action6_changed(self,value):
        self._mapping.call(5)        
    def _on_action7_changed(self,value):
        self._mapping.call(6)        
        
   
    def update(self):
        if (self.is_enabled()):
            self._update_on_off_button()
            #DeviceComponent._on_on_off_changed(self)            
        if self._update_callback != None:
            self._update_callback() 
        
        
    def _on_off_value(self, value):
        if (self.is_enabled()):
            DeviceComponent._on_off_value(self, value)
            self.show_device_parameters()
            
     
    def update_device_string(self):
        device_string = ' Browser selected'
        self._device_string = device_string
    
    def show_device_parameters(self):
        self.show_device_values(False)
        
    def show_device(self):
        #self.debug('show device')
        self.update_device_string()
        if self.is_enabled() and SLBrowser._display != None:
            track_string = ''
            track_string = self._main_device._mixer._selected_tracks_string
                #if self.application().view.is_view_visible('Detail/DeviceChain') and self._device:
                    #self.application().view.focus_view('Detail/DeviceChain')                
            self._display.show_message_left(self._device_string, track_string, True)
    
 
    

        
    def show_device_values(self, pot_light=False):
        #self.debug('show device value')
        if not self.check_browser_init():
            return
        self.update_device_string()
        if self.is_enabled() and SLBrowser._display != None:
            if self._is_last_nav :
                device_string = ' Browser Selected'
                param_string = ''
                if self._parameter_controls != None:
                    self._active_menu=self.update_browser_lists(self.param_values[0],self.param_values[1],self.param_values[2],self.param_values[3],0,self.param_values[4])
                    (p_names, p_values) = self.build_display(self._active_menu)
                    (param_names_string,param_values_string) = self.build_display_strings(p_names, p_values)                
                    self._display.show_message_left(param_names_string, param_values_string, False, pot_light)
                else:
                    self._display.show_message_left(' Browser Selected', '', False, pot_light)


    def update_browser_lists(self,tags,devices,folder,items,dico_val,fine_tune):
        nav_selectors_pos = (tags,devices,folder,items)
        last_nav_selector_used = self._last_category_id
        option_selectors_pos = (dico_val,fine_tune)
        options = (False,False) #self._apha_mode,self._alpha_fine_tune_mode)
        (cat,idx) = self._active_browser.select_item_and_return_data_sources(nav_selectors_pos,last_nav_selector_used,option_selectors_pos,options)
        return (cat,idx)
        
    def build_display(self,active_menu):
        pname = [] 
        pvalue = []  
        cat=active_menu[0]
        idx=active_menu[1]
        try:
            for items in range(len(cat)) :
                last_id = min(1,(len(cat[items])-idx[items]))
                lpname = ()
                if cat[items] != () and cat[items] != [] and last_id > 0:
                    for x in range(last_id):
                        lpname += (cat[items][x+idx[items]],)
                    if (len(lpname) < 1):
                        for x in range(1-len(lpname)):
                            lpname += ('',)
                else:
                    for x in range(1):
                        lpname += ('',)
                pname.append(lpname)
                #self.debug(str(pname))
                lpvalue = ()
                if cat[items] != () and cat[items] != [] and (idx[items]+last_id) < len(cat[items]):
                    for x in range(min(1,len(cat[items])-(idx[items]+last_id))):
                        lpvalue += (cat[items][x+idx[items]+last_id],)
                    if (len(lpvalue) < 1):
                        for x in range(1-len(lpvalue)):
                            lpvalue += ('',)
                else:
                    for x in range(1):
                        lpvalue += ('',)
                pvalue.append(lpvalue)            
                #self.debug(str(pvalue))
        except: 
            self.debug('Error in browsing')
            for items in range(len(cat)) :
                self.debug(str(cat[items]))
                self.debug(str(idx[items]))
        return ( pname , pvalue) 
        
    def build_display_strings(self,p_names,p_values):
        param_names_string = self.build_display_string( '<Browsing',p_names)    
        param_values_string = self.build_display_string('<Mode    ',p_values) 
        return (param_names_string,param_values_string) 
        
    def build_display_string(self,header,p_names):
        disp_string = ''
        if p_names != []:            
            for index in range(4):
                val = ' '
                if len(p_names[index]) > 0:
                    val = unicode(p_names[index][0])
                    if (self._last_category_id == index):
                        val = SLBrowser._display._adjust_strip_string(val,length=NUM_CHARS_PER_DISPLAY_LINE/2)                        
                    else:
                        val = SLBrowser._display._adjust_strip_string(val,length=NUM_CHARS_PER_DISPLAY_LINE/8)                        
                else:
                    val = ' '
                    if (self._last_category_id == index):
                        val = SLBrowser._display._adjust_strip_string(val,length=NUM_CHARS_PER_DISPLAY_LINE/2)                        
                    else:
                        val = SLBrowser._display._adjust_strip_string(val,length=NUM_CHARS_PER_DISPLAY_LINE/8) 
                disp_string += val    
        return disp_string
        
    def OLD_show_device_values(self, pot_light=False):
        #self.debug('show device value')
        self.update_device_string()
        if self.is_enabled() and SLBrowser._display != None:
            device_string = ' Browser Selected'
            param_string = ''
            if self._parameter_controls != None:
                self._active_menu=self.OLD_update_browser_lists(self.param_values[0],self.param_values[1],self.param_values[2],self.param_values[3],self.param_values[4],self.param_values[5],self.param_values[7])
                (p_names, p_values) = self.OLD_build_display(self._active_menu)
                (param_names_string,param_values_string) = self.OLD_build_display_strings(p_names, p_values)                
                self._display.show_message_left(param_names_string, param_values_string, False, pot_light)
            else:
                self._display.show_message_left(' Browser Selected', '', False, pot_light)
                

    
    def OLD_update_browser_lists(self,tags,devices,folder,items,dico_val,recent,fine_tune):
        nav_selectors_pos = (tags,devices,folder,items)
        last_nav_selector_used = self._last_category_id
        option_selectors_pos = (dico_val,fine_tune)
        options = (self._apha_mode,self._alpha_fine_tune_mode)
         
        if not self._recent_list_mode: #Live Full Browsing        
            (cat,idx) = self._active_browser.select_item_and_return_data_sources(nav_selectors_pos,last_nav_selector_used,option_selectors_pos,options)
        else:  #recent browsing mode  
            def _convert_midi_value_in_scale(value,scale,midirange=127):
                idx = (value * scale) / midirange
                return idx
            def _convert_midi_value_in_index(value,array,midirange=127):
                idx = _convert_midi_value_in_scale(value,len(array)-1,midirange)
                return idx
            tag_to_use = ''
            device_to_use = ''
            if self._hotswap_mode:
                (tag_to_use,device_to_use) = BrowserActions().get_filter_for_device()
            self._recent_list=self._recentpresets.build_one_for_all_list(tag_to_use,device_to_use)
            self._recent_idx = _convert_midi_value_in_index(recent,self._recent_list[0])
            cat = [
             self._recent_list[0],
             self._recent_list[0],
             self._recent_list[0],
             self._recent_list[0] ]
            
            #self.debug(str(self._recent_list[0]))
            idx = [
             self._recent_idx,
             self._recent_idx,
             self._recent_idx,
             self._recent_idx ]

        return (cat,idx)
        
    def OLD_build_display(self,active_menu):
        pname = [] 
        pvalue = []  
        cat=active_menu[0]
        idx=active_menu[1]
        try:
            for items in range(len(cat)) :
                last_id = min(self._view_zoom_factor,(len(cat[items])-idx[items]))
                lpname = ()
                if cat[items] != () and cat[items] != [] and last_id > 0:
                    for x in range(last_id):
                        lpname += (cat[items][x+idx[items]],)
                    if (len(lpname) < self._view_zoom_factor):
                        for x in range(self._view_zoom_factor-len(lpname)):
                            lpname += ('',)
                else:
                    for x in range(self._view_zoom_factor):
                        lpname += ('',)
                pname.append(lpname)
                #self.debug(str(pname))
                lpvalue = ()
                if cat[items] != () and cat[items] != [] and (idx[items]+last_id) < len(cat[items]):
                    for x in range(min(self._view_zoom_factor,len(cat[items])-(idx[items]+last_id))):
                        lpvalue += (cat[items][x+idx[items]+last_id],)
                    if (len(lpvalue) < self._view_zoom_factor):
                        for x in range(self._view_zoom_factor-len(lpvalue)):
                            lpvalue += ('',)
                else:
                    for x in range(self._view_zoom_factor):
                        lpvalue += ('',)
                pvalue.append(lpvalue)            
                #self.debug(str(pvalue))
        except: 
            self.debug('Error in browsing')
            for items in range(len(cat)) :
                self.debug(str(cat[items]))
                self.debug(str(idx[items]))
        return ( pname , pvalue)

    def OLD_build_display_string(self,p_names,p_values):
        param_names_string = ''
        param_values_string = ''
        for index in range(self._view_zoom_factor):
            if p_names != []:
                val = unicode(p_names[self._last_category_id][index])
                if self._last_category_id == 2 and self._active_browser.is_a_folder(unicode(p_names[0][0]),unicode(p_names[1][0]),unicode(p_names[self._last_category_id][index])):
                    val += '>'
                param_names_string += SLBrowser._display._adjust_strip_string(val,length=NUM_CHARS_PER_DISPLAY_LINE/self._view_zoom_factor)
            if p_values != []:
                val = unicode(p_values[self._last_category_id][index])
                if self._last_category_id == 2 and self._active_browser.is_a_folder(unicode(p_names[0][0]),unicode(p_names[1][0]),unicode(p_values[self._last_category_id][index])):
                    val += '>'
                param_values_string += SLBrowser._display._adjust_strip_string(val,length=NUM_CHARS_PER_DISPLAY_LINE/self._view_zoom_factor)
        return (param_names_string,param_values_string)       
        
       
    RECENT_SUPPORTED_TAGS = SLLiveCoreLibMenu.SUPPORTED_TAGS #('Drums', 'Instruments', 'Audio Effects', 'MIDI Effects', 'Max for Live')
    def _on_enter(self,active_menu):
        #self.debug(str(active_menu))
        menu=active_menu[0]
        idx=active_menu[1]
        if self._browser_mode != 4 and len(menu[0]) != 0:
            if True: #not self._recent_list_mode:
                self._main_actions(self._active_browser,active_menu)            
                lbrowsername = menu[0][idx[0]]
                if lbrowsername in SLBrowser.RECENT_SUPPORTED_TAGS:
                    ldevicename = menu[1][idx[1]]
                    ldevice = self._active_browser.get_topmenuentry_from_name(lbrowsername,menu[1][idx[1]])
                    if not (self._active_browser.is_a_folder(lbrowsername,menu[1][idx[1]],menu[2][idx[2]])):
                        lpreset = self._active_browser.get_menuitem_from_name(lbrowsername,menu[1][idx[1]],menu[2][idx[2]])
                        lfoldername = ''
                        lpresetname = menu[2][idx[2]]
                    else:
                        lfoldername = menu[2][idx[2]]
                        lpresetname = menu[3][idx[3]]                        
                        lpreset = self._active_browser.get_menuitem_in_folder_from_name(lbrowsername,menu[1][idx[1]],lfoldername,menu[3][idx[3]])
                        
                    self._recentpresets.add_item_to_recent_list(lbrowsername, ldevicename,ldevice,lfoldername,lpresetname,lpreset)
            # else:
                # if self._recent_list[1][self._recent_idx][5] != None:
                    # loaded = self._recent_list[1][self._recent_idx][5]
                    # BrowserActions().load(loaded)
                # else:
                    # pass
            if self._hotswap_mode:
                if self.application().view.browse_mode:
                    self.application().view.toggle_browse()
                #self.application().view.toggle_browse()
                self._hotswap_mode = not(self._hotswap_mode)
                self.force_mode_selector(9)
        else:
            self._main_actions(self._active_browser,active_menu)            
        self.show_device_values()
    
    def _on_alternate(self,active_menu):
        #self.debug(str(active_menu))
        menu=active_menu[0]
        idx=active_menu[1]
        if self._browser_mode != 4 and len(menu[0]) != 0:
            if True: #not self._recent_list_mode:
                self._alternate_actions(self._active_browser,active_menu)            
            # else:
                # if self._recent_list[1][self._recent_idx][5] != None:
                    # #loaded = self._recent_list[1][self._recent_idx][5]
                    # #BrowserActions().load(loaded)
                    # pass
                # else:
                    # pass
            if self._hotswap_mode:
                if self.application().view.browse_mode:
                    self.application().view.toggle_browse()
                #self.application().view.toggle_browse()
                self._hotswap_mode = not(self._hotswap_mode)
                self.force_mode_selector(9)
        else:
            self._alternate_actions(self._active_browser,active_menu)            
        self.show_device_values()
        
    def _main_actions(self,active_browser,active_menu):
        loaded = None
        loaded_name = ''
        
        lbrowser = ''
        ldevice = {}
        lfolder = ''
        lpreset = {}
        menu=active_menu[0]
        idx=active_menu[1]        
        
        if self._last_category_id == 0:
            pass
        elif self._last_category_id == 1:
            #not OK for Max 4 Live instruments & Plugins
            loaded = active_browser.call_action(True)
        else:                
            if self._last_category_id == 2:            
                if not (active_browser.is_a_folder(menu[0][idx[0]],menu[1][idx[1]],menu[2][idx[2]])):
                    loaded = active_browser.call_action(False)
            elif self._last_category_id == 3:
                #KO for plugins
                if (active_browser.is_a_folder(menu[0][idx[0]],menu[1][idx[1]],menu[2][idx[2]])):
                    #self.debug(str(self._selected_folder))
                    loaded = active_browser.call_action(False)
            else:
                raise AssertionError #should not happen since recent list mode is managed out of SLMenu
 
    def _alternate_actions(self,active_browser,active_menu):
        loaded = None
        loaded_name = ''
        
        lbrowser = ''
        ldevice = {}
        lfolder = ''
        lpreset = {}
        menu=active_menu[0]
        idx=active_menu[1]        
        
        if self._last_category_id == 0:
            pass
        elif self._last_category_id == 1:
            #not OK for Max 4 Live instruments & Plugins
            loaded = active_browser.call_action(True,False)
        else:                
            if self._last_category_id == 2:            
                if not (active_browser.is_a_folder(menu[0][idx[0]],menu[1][idx[1]],menu[2][idx[2]])):
                    loaded = active_browser.call_action(False,False)
            elif self._last_category_id == 3:
                #KO for plugins
                if (active_browser.is_a_folder(menu[0][idx[0]],menu[1][idx[1]],menu[2][idx[2]])):
                    #self.debug(str(self._selected_folder))
                    loaded = active_browser.call_action(False,False)
            else:
                raise AssertionError #should not happen since recent list mode is managed out of SLMenu
                    
  
    def create_hotswap_browser(self):
        tag_to_use = ''
        device_to_use = ''            
        (tag_to_use,device_to_use) = BrowserActions(parent=self.__parent).get_filter_for_device()
        if tag_to_use != '' and device_to_use != '':       
            return SLLiveHotswapPresetsMenu(tag_to_use,device_to_use,self.__parent)
        else:
            return None
            
    def _select_browser(self):
        
        if self._browser_mode == 0:
            # self._view_zoom_factor = self._previous_view_zoom_factor
            return self._corelib
        elif self._browser_mode == 1:
            # self._view_zoom_factor = self._previous_view_zoom_factor
            return self._favoritepresets
        elif self._browser_mode == 2:
            # self._view_zoom_factor = self._previous_view_zoom_factor
            return self._recentpresets
        elif self._browser_mode == 3:
            # self._view_zoom_factor = self._previous_view_zoom_factor
            _hotswp = self.create_hotswap_browser()
            if _hotswp != None:
                return _hotswp
            else:
                # force browser mode
                self._browser_mode = 0
                return self._corelib
        elif self._browser_mode == 4:
            # self._previous_view_zoom_factor = self._view_zoom_factor
            # self._view_zoom_factor = 1        
            return self._custommenu
            
    def _init_browser(self):
        self._browser_mode = 0
        self.param_values = [ 0,0,0,0,0,0,0,0];
        self._last_category_id = 0
        # self._apha_mode = False
        # self._alpha_fine_tune_mode = False
        # self._view_zoom_factor = NUM_CONTROLS_PER_ROW
        # self._previous_view_zoom_factor = self._view_zoom_factor
        # self._recent_list_mode = False
        self._hotswap_mode = False
         
        self._recent_idx = 0
        self._corelib = None
        #self._corelib.set_global_alternate_action(self._temp_alternate_action)
        self._favoritepresets = None
        self._recentpresets = None
        self._custommenu = None
        self._active_menu = None
        
    def _load_browser(self):            
        self._corelib = SLLiveCoreLibMenu(auto_refresh_folder_prefix=AUTO_REFRESH_FOLDER_PREFIX,parent=self.__parent)
        #self._corelib.set_global_alternate_action(self._temp_alternate_action)
        self._favoritepresets = SLFavoriteLivePresetsMenu(CoreLib=self._corelib,parent=self.__parent)
        self._recentpresets = SLRecentLivePresetsMenu(CoreLib=self._corelib,FavLib=self._favoritepresets,parent=self.__parent)
        self._custommenu = SLGlobalMenu(external_mapping=self._mapping,parent=self.__parent)
        self._active_menu = None        

    # def _temp_alternate_action(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry):
        # if lmenuentry != None:
            # BrowserActions('',parent=self.__parent).Insert_Clip(lmenuentry)
        # elif ltopmenuentry != None:
            # BrowserActions('',parent=self.__parent).Insert_Clip(ltopmenuentry)
    
    def _read_presets(self,f,header,corelib,func):
        
        lines = [line.strip() for line in f]
        step = 0
        lbrowser = ''
        ldevice = None
        lfolder = ''
        ldevicename = ''
        preset_name = ''
        lpreset = None
        for line in lines:
            if step == 0:
                if line[1:7]!=header:                    
                    return (lbrowser, ldevice,lfolder,lpreset)
            elif step == 1:
                #self.debug(line[6:-7])
                lbrowser = line[6:-7]                
            elif step == 2:
                #self.debug(line[8:-9])
                try :
                    ldevicename=line[8:-9]
                    ldevice = corelib.get_topmenuentry_from_name(lbrowser,ldevicename)
                except:
                    self.debug("failed to find preset in corelib")
                    lbrowser = ''
                    ldevicename = ''
                    ldevice = None
                    lfolder = ''
                    preset_name = ''
                    lpreset = None
                #self.debug('-> %s' % ldevice)
            elif step == 3:
                #self.debug(line[8:-9])
                lfolder = line[8:-9]
            elif step == 4:
                #self.debug(line[8:-9])
                try :
                    if lfolder != '':
                        preset_name = line[8:-9]
                        lpreset=corelib.get_menuitem_in_folder_from_name(lbrowser,ldevicename,lfolder,preset_name) #+'>' add '>' char at end of folder name read
                    else:
                        preset_name = line[8:-9]
                        lpreset = corelib.get_menuitem_from_name(lbrowser,ldevicename,preset_name)
                except :
                    self.debug("failed to find preset in corelib")
                    lbrowser = ''
                    ldevicename = ''
                    ldevice = None
                    lfolder = ''
                    preset_name = ''
                    lpreset = None
            elif step == 5:
                if lbrowser != '':
                    func(lbrowser, ldevicename,ldevice,lfolder,preset_name,lpreset)
            else:
                raise AssertionError
            step = (step +1)%6

        
    def _load_recent(self):
        if self._recentpresets != None:
            self._load_presets(RECENT_PRESETS_FILE,'RECENT',self._corelib,self._recentpresets.add_item_to_recent_list) 
        
    def _load_favorites(self):
        if self._favoritepresets != None:
            self._load_presets(FAVORITE_PRESETS_FILE,'MARKED',self._corelib,self._favoritepresets.add_item_to_favorites_list)
        
    def _load_presets(self,filename,header,corelib,func):
        mrs_path = ''
        for path in sys.path:
            if 'MIDI Remote Scripts' in path:
                mrs_path = path
                break
        user_file = mrs_path + '/SL_Ultimate_Control_Browser/' + filename
        #self.debug(user_file)
        try:
            f = open(user_file,'r')
        except:
            self.debug("failed to open recent/favorites file : %s" % filename)
            return ('',None,'',None)
        
        self._read_presets(f,header,corelib,func)
        f.close()
        
    def _save_recent(self):
        if self._recentpresets != None:
            self._save_presets(RECENT_PRESETS_FILE,self._recentpresets,'RECENT')
    
    def _save_favorites(self):
        if self._favoritepresets != None:
            self._save_presets(FAVORITE_PRESETS_FILE,self._favoritepresets,'MARKED')
    
    def _save_presets(self,filename,browser,header):
        try:
            mrs_path = ''
            for path in sys.path:
                if 'MIDI Remote Scripts' in path:
                    mrs_path = path
                    break
            user_file = mrs_path + '/SL_Ultimate_Control_Browser/' + filename
            #self.debug(user_file)
            f = open(user_file,'w')
        except: 
            self.debug('error in opening file %s for saving presets' % filename)
            return None
        presets_list=browser.build_one_for_all_list()
        if presets_list[1] != None:
            for preset in presets_list[1]:
                self._write_preset(f,preset,browser,header)   
        f.close()
        
    def _write_preset(self,f,preset,browser,header):
        f.write('<'+header+'>\n')
        f.write('<TAGS>%s</TAGS>\n' % preset[0])
        f.write('<DEVICE>%s</DEVICE>\n' % preset[1])
        if preset[5] != None:
            folder=preset[3]
            #if folder != '':
            #    folder=folder[:-1] #remove '>' char at end of folder name
            f.write('<FOLDER>%s</FOLDER>\n' % folder)
            preset_name = preset[4]
            f.write('<PRESET>%s</PRESET>\n' % preset_name)
        else:
            f.write('<FOLDER>%s</FOLDER>\n' % '')
            preset_name = preset[4]
            f.write('<PRESET>%s</PRESET>\n' % preset_name)
        f.write('</'+header+'>\n')        
    
    def _autosave_mappings(self):
        mrs_path = ''
        for path in sys.path:
            if 'MIDI Remote Scripts' in path:
                mrs_path = path
                break
        user_file = mrs_path + '/SL_Ultimate_Control_Browser/' + BACKUP_SETTINGS_FILE
        #self.debug(user_file)
        try:
            f = open(user_file,'w')
        except:
            self.debug('error in opening file %s for saving settings' % BACKUP_SETTINGS_FILE)
            return
        self._mapping.save(f)
        f.close()
    def _load_last_mappings(self):
        mrs_path = ''
        for path in sys.path:
            if 'MIDI Remote Scripts' in path:
                mrs_path = path
                break
        user_file = mrs_path + '/SL_Ultimate_Control_Browser/' + BACKUP_SETTINGS_FILE
        #self.debug(user_file)
        try:
            f = open(user_file,'r')
        except:
            self.debug("failed to open settings file : %s" % BACKUP_SETTINGS_FILE)
            return
        self._mapping.load(f)
        f.close()