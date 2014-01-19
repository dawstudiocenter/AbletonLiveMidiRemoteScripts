DEBUG = False

class SLMenuWithActions():

    #Virtual Layout 
    #
    #[topmenu1] <= no action possible           ......                 [topmenu2]
    #    |   
    #    - [topmenuentry1] <= action allowed (is an object + a name attribute)
    #    |      |            
    #    |      - [menufolder] <= no action possible
    #    |      |       |            
    #    |      |       - [folder_menuitem1] <= action allowed (is an object + a name attribute)
    #    |      |       |            
    #    |      |       - [folder_menuitem2] <= action allowed (is an object + a name attribute)
    #    |      |       |            
    #    |      |       - [...]
    #    |      |            
    #    |      - [menuitem1] <= action allowed (is an object + a name attribute)
    #    |      |            
    #    |      - [menuitem2] <= action allowed (is an object + a name attribute)
    #    |                  
    #    - [topmenuentry2]
    #    |   
    #    - [...]
    #
    #
    #    
    #BROWSER GENERAL STRUCTURE
    #BROWSER[] = {key=topmenuX (ascii), value={'topmenu' : topmenuX (ascii), 'topmenuentries' : TOPMENUENTRIES[] } }      
    #TOPMENUENTRIES[] = {key=topmenuentryX (ascii), value={'topmenuentryobject' : topmenuentryXObject (name=ascii,others), 'menuitems' : MENUITEMS[], 'menufolders' : MENUFOLDERS[]}
    #MENUITEMS[]= { key=menuitemX (ascii),value=menuitemXObject(name=ascii,others)}
    #MENUFOLDERS[] = {key=menufolder (ascii),value=FOLD_ITEMS[]}
    #FOLD_ITEMS= { key=menuitemX (ascii),value=menuitemXObject(name=ascii,others)}

    
    def __init__(self,global_main_action=None, global_alternate_action=None,parent=None):
        self.__parent = parent
        self._global_main_action = global_main_action
        self._global_alternate_action = global_alternate_action
        self._browser = {}
        self._browser_action = {}
        self.columns = None
        self.columns_idx = 0
        self._topmenuentryfilter = ''
        self._topmenufilter=''
        if DEBUG:
            self._builtin_test()
            self._browser = {}
            self._browser_action = {}

    def set_global_alternate_action(self,func):
        self._global_alternate_action = func
    def set_global_main_action(self,func):
        self._global_main_action = func
        
    def _debug(self,msg):
        if self.__parent != None:
            s = msg.encode('utf-8')
            return self.__parent.log_message(s)
    
    def _starts_with(self, str, prefix):
        #Returns whether or not the given string starts with the given prefix.
        return not(str.find(prefix, 0,len(prefix)) == -1)
        
    def _ends_with(self, str, suffix):
        #Returns whether or not the given string ends with the given suffix.
        return not(str.find(suffix, len(str) - len(suffix)) == -1)       
             
    def add_item(self,ltopmenu,ltopmenuentryname,ltopmenuentry,lmenufolder,lmenuentryname,lmenuentry):
        """ Add a menu entry
            ltopmenu is the ascii name of the topmenu,
            ltopmenuentryname is the ascii name of the topmenuentry 
            ltopmenuentry is an object,
            lmenufolder is the ascii name of the menufolder,
            lmenuentryname is the ascii name of the menuentry,
            lmenuentry is an object,
            marked is a flag to customize ascii name name of lmenuentry or ltopmenuentry 
            """
        def _add( self,ltopmenu,ltopmenuentryname,ltopmenuentry,lmenufolder,lmenuentryname,lmenuentry):          
            if ltopmenuentry !=None:
                if lmenuentry!=None:
                    if lmenufolder!='':
                        fold_menuitem = { lmenuentryname:lmenuentry }
                        fold = { lmenufolder:fold_menuitem } #{ lmenufolder+'>':fold_menuitem }
                        menuitem = {}
                    else:
                        fold = {}
                        menuitem = {lmenuentryname:lmenuentry}                    
                elif lmenufolder != '':
                    fold_menuitem = {}
                    fold = { lmenufolder:fold_menuitem } #{ lmenufolder+'>':fold_menuitem }
                    menuitem = {}
                else:
                    fold = {}
                    menuitem = {}
            else:
                fold = {}
                menuitem = {}
                
            if ltopmenu in self._browser.keys():
                if self._browser[ltopmenu]['topmenuentries']!=None:
                    if ltopmenuentry != None:                
                        if ltopmenuentryname in self._browser[ltopmenu]['topmenuentries'].keys():
                            if not(lmenufolder != ''):
                                if self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menuitems']!=None:
                                    if lmenuentry !=None:
                                        if not lmenuentryname in self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menuitems'].keys():
                                            self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menuitems'] = dict(self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menuitems'].items() + menuitem.items())
                                    else:
                                        pass # nothing to do
                                else: #create new menuitems
                                    self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menuitems'] = menuitem
                            else:
                                if self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menufolders']!=None:
                                    if (lmenufolder) in self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menufolders'].keys(): #lmenufolder+'>'
                                        self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menufolders'][lmenufolder] = dict(self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menufolders'][lmenufolder].items() + fold_menuitem.items()) #lmenufolder+'>'
                                    else: #append topmenufolder
                                        self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menufolders'] = dict (self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menufolders'].items() + fold.items())
                                else: #create new topmenufolders
                                    self._browser[ltopmenu]['topmenuentries'][ltopmenuentryname]['menufolders'] = fold
                        else: #append new topmenuentry
                            dev = { 'topmenuentryobject' : ltopmenuentry, 'menuitems' : menuitem, 'menufolders' : fold}
                            devs = { ltopmenuentryname:dev}
                            self._browser[ltopmenu]['topmenuentries'] = dict(self._browser[ltopmenu]['topmenuentries'].items() + devs.items())
                    else:
                        devs = {}
                        self._browser[ltopmenu]['topmenuentries'] = devs
                else: # create new topmenuentries
                    dev = { 'topmenuentryobject' : ltopmenuentry, 'menuitems' : menuitem, 'menufolders' : fold}
                    devs = { ltopmenuentryname:dev}
                    self._browser[ltopmenu]['topmenuentries'] = devs
            else: # create all
                if ltopmenuentry != None:
                    dev = { 'topmenuentryobject' : ltopmenuentry, 'menuitems' : menuitem, 'menufolders' : fold}
                    self._browser[ltopmenu] = { 'topmenu' : ltopmenu, 'topmenuentries' : { ltopmenuentryname:dev}}
                else:
                    devs = {}
                    self._browser[ltopmenu] = { 'topmenu' : ltopmenu, 'topmenuentries' : {}}
        
        _add(self,ltopmenu,ltopmenuentryname,ltopmenuentry,lmenufolder,lmenuentryname,lmenuentry)
        
    def remove_item(self,ltopmenu,ltopmenuentryname,lmenufolder,lmenuentryname):

        def _remove(self,ltopmenu,topmenuentryname,lmenufolder,menuentryname):
            menufolder=lmenufolder

            if ltopmenu in self._browser.keys():
                if self._browser[ltopmenu]['topmenuentries']!=None:
                    if topmenuentryname != '':
                        if topmenuentryname in self._browser[ltopmenu]['topmenuentries'].keys():
                            if menuentryname != '':
                                if menufolder == '':
                                    if self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menuitems']!=None:
                                        if  menuentryname in self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menuitems'].keys():
                                            del self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menuitems'][menuentryname]
                                            del self._browser_action[ltopmenu+topmenuentryname+menuentryname]
                                        else:
                                            pass #not found
                                    else:
                                            pass #not found
                                else:
                                    if self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menufolders']!=None:
                                        if menufolder in self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menufolders'].keys():
                                            if menuentryname in self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menufolders'][menufolder].keys():
                                                del self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menufolders'][menufolder][menuentryname]
                                                del self._browser_action[ltopmenu+topmenuentryname+menufolder+menuentryname]
                                            else:
                                                pass #not found
                                        else:
                                            pass #not found
                            elif menufolder != '':
                                if self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menufolders']!=None:
                                    if menufolder in self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menufolders'].keys():
                                        del self._browser[ltopmenu]['topmenuentries'][topmenuentryname]['menufolders'][menufolder]
                                        for actions in self._browser_action.keys():
                                            if self._starts_with(actions,ltopmenu+topmenuentryname+menufolder):
                                                del self._browser_action[actions]
                                    else:
                                        pass #not found
                                else:
                                    pass #not found
                            else:
                                del self._browser[ltopmenu]['topmenuentries'][topmenuentryname]
                                for actions in self._browser_action.keys():
                                    if self._starts_with(actions,ltopmenu+topmenuentryname):
                                        del self._browser_action[actions]
                        else:
                            pass # not found
                    else:
                        del self._browser[ltopmenu]
                        for actions in self._browser_action.keys():
                            if self._starts_with(actions,ltopmenu):
                                del self._browser_action[actions]

        _remove(self,ltopmenu,ltopmenuentryname,lmenufolder,lmenuentryname)

    def register_main_callback(self,func,ltopmenu,ltopmenuentryname,lmenufolder,lmenuentryname):
        self._register_callback('main',func,ltopmenu,ltopmenuentryname,lmenufolder,lmenuentryname)
    def register_alternate_callback(self,func,ltopmenu,ltopmenuentryname,lmenufolder,lmenuentryname):
        self._register_callback('alternate',func,ltopmenu,ltopmenuentryname,lmenufolder,lmenuentryname)
    def _register_callback(self,type,func,ltopmenu,ltopmenuentryname,lmenufolder,lmenuentryname):
      
        if ltopmenu != '' and ltopmenuentryname != '' :
            if lmenuentryname != '' :
                if (lmenufolder != '' and (lmenuentryname in self.get_folditems_names_for_folder(ltopmenu,ltopmenuentryname,lmenufolder))) or (lmenufolder == '' and (lmenuentryname in self.get_menuitems_names_from_name(ltopmenu,ltopmenuentryname))):
                    if (ltopmenu + ltopmenuentryname + lmenufolder + lmenuentryname) not in self._browser_action.keys():
                        self._browser_action[ltopmenu + ltopmenuentryname + lmenufolder + lmenuentryname] = { 'main' : None, 'alternate' : None}
                    self._browser_action[ltopmenu + ltopmenuentryname + lmenufolder + lmenuentryname][type] = func
            else:
                if ltopmenuentryname in self.get_topmenuentries_names_from_name(ltopmenu):
                    if (ltopmenu + ltopmenuentryname + lmenufolder + lmenuentryname) not in self._browser_action.keys():
                        self._browser_action[ltopmenu + ltopmenuentryname] = { 'main' : None, 'alternate' : None}
                    self._browser_action[ltopmenu + ltopmenuentryname][type] = func

#for action, additional parameters is required to allow further management of item in browser list (topmenu, menuentryname, menuentry...)    
    def call_action(self,topmenuaction,mainaction=True):
        """ used to call main/alternate action on selected item that is memorized """
        if len(self.columns[0]) != 0:
            ltopmenu=self.columns[0][self.columns_idx[0]]
        else:
            ltopmenu = ''
        if len(self.columns[1]) != 0:
            ltopmenuentryname=self.columns[1][self.columns_idx[1]]
        else:
            ltopmenuentryname = ''
        if len(self.columns[2]) != 0:
            lmenuitem_or_foldername=self.columns[2][self.columns_idx[2]]
        else:
            lmenuitem_or_foldername = ''
        if len(self.columns[3]) != 0:
            lfolderitemname=self.columns[3][self.columns_idx[3]]
        else:
            lfolderitemname = ''
        laction_name = ltopmenu + ltopmenuentryname + lmenuitem_or_foldername + lfolderitemname
        if ltopmenuentryname != '':
            if mainaction:
                if self._global_main_action != None:            
                    _action_func = self._global_main_action
                else:
                    _action_func = self._get_action(laction_name,'main')
            else:            
                if self._global_alternate_action != None:               
                    _action_func = self._global_alternate_action
                else:
                    _action_func = self._get_action(laction_name,'alternate')
            
        if _action_func != None :
            if topmenuaction:
                if ltopmenuentryname != '':
                    _action_func(ltopmenu,ltopmenuentryname,self.get_topmenuentry_from_name(ltopmenu,ltopmenuentryname),'','',None)
            else:                
                if not (self.is_a_folder(ltopmenu,ltopmenuentryname,lmenuitem_or_foldername)):
                    _action_func(ltopmenu,ltopmenuentryname,self.get_topmenuentry_from_name(ltopmenu,ltopmenuentryname),'',lmenuitem_or_foldername,self.get_menuitem_from_name(ltopmenu,ltopmenuentryname,lmenuitem_or_foldername))
                else:
                    _action_func(ltopmenu,ltopmenuentryname,self.get_topmenuentry_from_name(ltopmenu,ltopmenuentryname),lmenuitem_or_foldername,lfolderitemname,self.get_menuitem_in_folder_from_name(ltopmenu,ltopmenuentryname,lmenuitem_or_foldername,lfolderitemname))
    def _get_action(self,actioname,type):
        if actioname in self._browser_action.keys():
            return self._browser_action[actioname][type]
        else:
            return None
    def get_topmenu(self,ltopmenuname):
        """ Returns the topmenu from name """
        return self._browser[ltopmenuname]
    def get_topmenus_names(self):
        """ Returns the list of topmenus names """
        return sorted(self._browser.keys())
    def get_topmenuentries_names_from_name(self,ltopmenuname):
        """ Returns the list of topmenuentries names for a topmenu """
        return sorted(self._browser[ltopmenuname]['topmenuentries'].keys())
    def get_folders_names_from_name(self, ltopmenuname,ltopmenuentryname):
        """ Returns the list of menufolders names for the given topmenuentry
        and stores the selected topmenuentry. """
        if ltopmenuentryname in self._browser[ltopmenuname]['topmenuentries'].keys():
            _selected_topmenuentry = self._browser[ltopmenuname]['topmenuentries'][ltopmenuentryname]
            return sorted(_selected_topmenuentry['menufolders'].keys())
        else:
            return ()
    def get_menuitems_names_from_name(self, ltopmenuname,ltopmenuentryname):
        """ Returns the list of menufolders names for the given topmenuentry and stores the selected topmenuentry. """
        if ltopmenuentryname in self._browser[ltopmenuname]['topmenuentries'].keys():
            _selected_topmenuentry = self._browser[ltopmenuname]['topmenuentries'][ltopmenuentryname]
            return sorted(_selected_topmenuentry['menuitems'])
        else:
            return ()            
    def get_listof_menuitem_and_folder_names_from_name(self, ltopmenuname,ltopmenuentryname):
        """ Returns the list of menufolders and menuitems names for the given topmenuentry and stores the selected topmenuentry. """
        _selected_topmenuentry = self._browser[ltopmenuname]['topmenuentries'][ltopmenuentryname]
        return sorted(_selected_topmenuentry['menufolders'].keys()) + sorted(_selected_topmenuentry['menuitems'])        
    def is_a_folder(self,ltopmenuname,ltopmenuentryname,lmenuitem):        
        if ltopmenuname != '' and ltopmenuentryname != '' and lmenuitem in self._browser[ltopmenuname]['topmenuentries'][ltopmenuentryname]['menufolders'].keys(): # self._ends_with('%s' % lmenuitem , '>'):
            return True
        else:
            return False
    def get_folditems_names_for_folder(self, ltopmenuname,ltopmenuentryname,lfoldername):        
        if ltopmenuentryname in self._browser[ltopmenuname]['topmenuentries'].keys():
            _selected_topmenuentry = self._browser[ltopmenuname]['topmenuentries'][ltopmenuentryname]
            _selected_folder = _selected_topmenuentry['menufolders'][lfoldername]
            return sorted(_selected_folder.keys())
        else:
            return ()

    def get_topmenuentry_from_name(self, ltopmenu,ltopmenuentryname):
        """ Returns the topmenuentry object for the given topmenu name and topmenuentry name. """
        if ltopmenuentryname in self._browser[ltopmenu]['topmenuentries'].keys():
            _selected_topmenu = self._browser[ltopmenu]
            return _selected_topmenu['topmenuentries'][ltopmenuentryname]['topmenuentryobject']
        else:
            return ()
    def get_listof_topmenuentries_for_topmenu(self, ltopmenuname):
        """ Returns the list of topmenuentries for the given topmenu and stores the topmenu. """
        selected_topmenu = self._browser[ltopmenuname]
        return sorted(self._selected_topmenu['topmenuentries'])
    def get_menuitem_from_name(self, ltopmenu,ltopmenuentryname,lmenuentryname):
        """ Returns the menuitem object for the given topmenu name topmenuentry name, and menuentryname. """
        selected_topmenu = self._browser[ltopmenu]        
        selected_topmenuentry = selected_topmenu['topmenuentries'][ltopmenuentryname]
        return selected_topmenuentry['menuitems'][lmenuentryname]
    def get_menuitem_in_folder_from_name(self,ltopmenu,ltopmenuentryname,lfoldername,lmenuentryname):
        """ Returns the in folder menuitem object for the given topmenu name topmenuentry name, folder name and menuentry name. """
        selected_topmenu = self._browser[ltopmenu]
        selected_topmenuentry = selected_topmenu['topmenuentries'][ltopmenuentryname]
        selected_folder = selected_topmenuentry['menufolders'][lfoldername]
        return selected_folder[lmenuentryname]   

  
    def _builtin_test_message(self,name,object):
        print (name + ' - ' + str(object))
                
    def _builtin_test(self):
        class test_object():
            name = ''
            others = 1234
            def __init__(self,name):
                self.name = name
                   
        BITE = 'BITE - '
        STEP = 1
        def HEAD():
            return (str(BITE) + str(STEP) + ' :')
        self.add_item('Menu1','',None,'','',None)
        print (HEAD()+str(self._browser))
        STEP = 2
        sample_topmenuentry=test_object('TopMenuEntry1')
        self.add_item('Menu2',sample_topmenuentry.name,sample_topmenuentry,'','',None)
        self.register_main_callback(SLMenuWithActions._builtin_test_message,'Menu2',sample_topmenuentry.name,'','')
        print (HEAD()+str(self._browser))
        STEP = 3
        sample_menuitem=test_object('MenuItem1')
        sample2_topmenuentry=test_object('TopMenuEntry2')
        self.add_item('Menu2',sample2_topmenuentry.name,sample2_topmenuentry,'',sample_menuitem.name,sample_menuitem)
        self.register_alternate_callback(SLMenuWithActions._builtin_test_message,'Menu2',sample2_topmenuentry.name,'','')
        print (HEAD()+str(self._browser))
        STEP = 4
        sample2_menuitem=test_object('MenuItem2')
        sample3_topmenuentry=test_object('TopMenuEntry3')
        self.add_item('Menu3',sample3_topmenuentry.name,sample3_topmenuentry,'samplefolder1',sample2_menuitem.name,sample2_menuitem)
        self.register_alternate_callback(SLMenuWithActions._builtin_test_message,'Menu3',sample3_topmenuentry.name,'samplefolder1',sample2_menuitem.name)
        print (HEAD()+str(self._browser))
        STEP = 5
        self.remove_item('Menu3','','','')
        if not self._browser.has_key('Menu3'):
            print(HEAD() + 'Remove TopMenu - OK')   
        else:
            print(HEAD() + 'Remove TopMenu - KO')   
        print (HEAD()+str(self._browser))
        STEP = 6
        self.remove_item('Menu2',sample2_topmenuentry.name,'','')
        if self._browser.has_key('Menu2') and not self._browser['Menu2']['topmenuentries'].has_key(sample2_topmenuentry.name):
            print(HEAD() + 'Removing TopMenuEntries - OK')   
        else:
            print(HEAD() + 'Removing TopMenuEntries - KO')   
        print (HEAD()+str(self._browser))
        STEP = 7
        print (HEAD()+str(self._browser_action))
        self._browser_action['Menu2'+sample_topmenuentry.name]['main'](self,HEAD() + 'Add action - OK',None)
        STEP = 8       
        if self._browser_action.has_key('Menu2'+sample_topmenuentry.name) and not self._browser_action.has_key('Menu2'+sample2_topmenuentry.name) and not self._browser_action.has_key('Menu3'+sample3_topmenuentry.name+'samplefolder1'+sample2_menuitem.name) :
            print(HEAD() + 'Remove action - OK')
        else:
            print(HEAD() + 'Remove action - KO')
   
        
    def set_filters(self,TopMenuFilter='',TopMenuEntryFilter=''):
        """ used to define a filter either on topmenu or topmenu entries or both  """
        self._topmenufilter=TopMenuFilter
        self._topmenuentryfilter = TopMenuEntryFilter
    
    def select_item_and_return_data_sources(self,nav_selectors_pos,last_nav_selector_used,option_selectors_pos,options):
        """ 
        compute, memorize and return a list of available data sources and the selected data index according to selectors and navigation options 
        nav_selector_pos shall contains the selector pos for each column in range(0-127)
        last_nav_selector provide the selector id used at last in range(0-3)
        options contains the active option alpha_mode and then alpha fine_tune_mode that will be applied to the last selected selector
        option_selector_pos provide the fine tune selector pos in range(0-127) that will applied to the last selected selector pos
        """
        if (len(nav_selectors_pos) != 4) or (len(option_selectors_pos) != 2) or (len(options) != 2):
            raise AssertionError
        
        _sel_topmenu=nav_selectors_pos[0] #tags
        _sel_topmenuentry=nav_selectors_pos[1] #devices
        _sel_menuitemsandfolders=nav_selectors_pos[2] #folder/items
        _sel_items=nav_selectors_pos[3] #items
        _sel_alpha=option_selectors_pos[0] #dico_val
        _sel_fine=option_selectors_pos[1] #fine_tune
        _alpha_mode=options[0]
        _alpha_fine_mode=options[1]
        _sel_id=last_nav_selector_used #last_category_id
        
            
        def _convert_midi_value_in_scale(value,scale,midirange=127):
            idx = (value * scale) / midirange
            return idx
            
        def _convert_midi_value_in_index(value,array,midirange=127):
            idx = _convert_midi_value_in_scale(value,len(array)-1,midirange)
            return idx
        
        def _adjust_value_with_fine_tune(value, max_val, fine_tune,min_val=0):
            val = max(min_val,min(max_val,value+_convert_midi_value_in_scale(fine_tune,7)))
            return val
            
        def _get_idx_to_jump_to_letter(letter_number,array): #starting at 0 for 1st letter
            idx = 0
            dico_chr = chr(ord('A') + letter_number+1)
            for i in array:                
                if (self._starts_with('%s' % i , dico_chr)):
                    break
                idx+=1
            return idx

        
        if _alpha_mode :                
            _sel_alpha = _convert_midi_value_in_scale(_sel_alpha,24)
            dico_chr = chr(ord('A') + _sel_alpha)
        
        # TOP MENU
        _topmenusnames = ()
        _topmenu_idx = 0
        if self._topmenufilter != '':
            _topmenusnames = (self._topmenufilter,)
            _topmenu_idx = 0 #((tags) * 1) / 127
        else:    
            _topmenusnames = self.get_topmenus_names()                
            _topmenu_idx = _convert_midi_value_in_index(_sel_topmenu,_topmenusnames)
        
        # TOPMENUENTRY
        _topmenuentrynames = ()
        _topmenuentry_idx = 0
        if len(_topmenusnames) != 0:             
            if self._topmenuentryfilter != '':
                self._selected_topmenuentry = self.get_topmenuentry_from_name(_topmenusnames[_topmenu_idx],self._topmenuentryfilter)
                _topmenuentrynames = (self._topmenuentryfilter,)
                _topmenuentry_idx = 0 #((devices) * 1) / 127                
            else:                    
                _topmenuentrynames = self.get_topmenuentries_names_from_name(_topmenusnames[_topmenu_idx])
                if len(_topmenuentrynames) != 0:
                    _topmenuentry_idx = _convert_midi_value_in_index(_sel_topmenuentry,_topmenuentrynames)
                    if _sel_id == 1: #apply fine_tune since it was the last select encoder used
                        self._topmenuentry_idx = _adjust_value_with_fine_tune(_topmenuentry_idx,len(_topmenuentrynames)-1,_sel_fine)
            
        # MENUFOLDERS/MENUITEMS
        _menuitem_and_foldernames = ()
        _menuitem_and_foldernames_idx = 0
        if len(_topmenuentrynames) != 0:
            _menuitem_and_foldernames = self.get_listof_menuitem_and_folder_names_from_name(_topmenusnames[_topmenu_idx],_topmenuentrynames[_topmenuentry_idx])
            if len(_menuitem_and_foldernames) != 0:
                _menuitem_and_foldernames_idx = _convert_midi_value_in_index(_sel_menuitemsandfolders,_menuitem_and_foldernames)
                if _sel_id == 2: #apply fine_tune since it was the last select encoder used
                    _menuitem_and_foldernames_idx = _adjust_value_with_fine_tune(_menuitem_and_foldernames_idx,len(_menuitem_and_foldernames)-1,_sel_fine)
                    if _alpha_mode : #jump directly to letter selected using dico encoder
                        _menuitem_and_foldernames_idx = min(_get_idx_to_jump_to_letter(_sel_alpha,_menuitem_and_foldernames),len(_menuitem_and_foldernames)-1)
                    if _alpha_fine_mode : #apply fine tune after jump directly to letter selected using dico encoder
                        _menuitem_and_foldernames_idx = _get_idx_to_jump_to_letter(_sel_alpha,_menuitem_and_foldernames)
                        _menuitem_and_foldernames_idx = _adjust_value_with_fine_tune(_menuitem_and_foldernames_idx,len(_menuitem_and_foldernames)-1,_sel_fine)
                
        # FOLDER_MENUITEMS
        _folditems = ()
        _folditems_idx = 0
        if len(_menuitem_and_foldernames) != 0:
            if self.is_a_folder(_topmenusnames[_topmenu_idx],_topmenuentrynames[_topmenuentry_idx], _menuitem_and_foldernames[_menuitem_and_foldernames_idx]):
                _folditems = self.get_folditems_names_for_folder(_topmenusnames[_topmenu_idx],_topmenuentrynames[_topmenuentry_idx],_menuitem_and_foldernames[_menuitem_and_foldernames_idx])
                if len(_folditems) != 0:
                    _folditems_idx = _convert_midi_value_in_index(_sel_items,_folditems)
                    if _sel_id == 3: #apply fine_tune since it was the last select encoder used
                        _folditems_idx = _adjust_value_with_fine_tune(_folditems_idx, len(_folditems)-1,_sel_fine)
                        if _alpha_mode :#jump directly to letter selected using dico encoder
                            _folditems_idx = min(_get_idx_to_jump_to_letter(_sel_alpha,_folditems),len(_folditems)-1)
                        if _alpha_fine_mode :#apply fine tune after jump directly to letter selected using dico encoder
                            _folditems_idx = _get_idx_to_jump_to_letter(_sel_alpha,_folditems)
                            _folditems_idx = _adjust_value_with_fine_tune(_folditems_idx,len(_folditems)-1,_sel_fine)

        self.columns = [_topmenusnames, _topmenuentrynames, _menuitem_and_foldernames, _folditems]
        self.columns_idx = [_topmenu_idx,_topmenuentry_idx,_menuitem_and_foldernames_idx,_folditems_idx]   
            
        return self.columns , self.columns_idx

    def build_one_for_all_list(self,TopMenuFilter='',TopMenuEntryFilter=''):
        recent_list = [[] for x in range(2)]
    
        #shall all Marked mgmt here
        for kt in self._browser.keys():
            if TopMenuFilter=='' or TopMenuFilter==kt:
                for kd,d in self._browser[kt]['topmenuentries'].items():
                    if TopMenuEntryFilter=='' or TopMenuEntryFilter==kd:
                        for kf,f in d['menufolders'].items():
                            for kp,p in f.items():
                                recent_list[0].append( '%s | %s | %s | %s' % (kt,kd,kf,kp)) #for display use
                                recent_list[1].append((kt,kd,d,kf,kp,p)) #for loading or for add/remove to/from favorites purpose
                        for kp,p in d['menuitems'].items():
                            recent_list[0].append( '%s | %s | %s' % (kt,kd,kp)) #for display use
                            recent_list[1].append((kt,kd,d,'',kp,p)) #for loading or for add/remove to/from favorites purpose
        if recent_list[0]==[]:
            recent_list[0] = ' '
            recent_list[1] = None
        
        return recent_list

#sample_menuaction = SLMenuWithActions(global_main_action=SLOptionsMenu._builtin_test_message)
#print(str(sample_menuaction._browser))
#print(str(sample_menuaction._browser_action))