import sys
import os
from SLMenus import SLMenuWithActions
from SLLiveActions import BrowserActions,TrackActions,SceneActions,GlobalActions,DummyActions,ClipActions
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from config import MIDI1_TRACK_COLOR,AUDIO_TRACK_COLOR,SETTINGS_FILE

  
class SLGlobalMenu(SLMenuWithActions,ControlSurfaceComponent):
    def __init__(self,external_mapping=None,parent=None):  #external mapping is an object used for pad mapping     
        SLMenuWithActions.__init__(self,parent=parent)
        ControlSurfaceComponent.__init__(self)
        self.parent=parent 
        self.external_mapping = external_mapping        
        self._active_learning_pad = None
        self.action = {}
        self._create_global_browser()
        self._create_tempo_action()
        self._create_quantize_action()
        self._create_record_quantize_action()
        self.create_shortcuts()
        self._rebuild_menu()
        
    def on_selected_track_changed(self):
        self._rebuild_menu()

    def on_selected_scene_changed(self):
        pass    

    def _main_action(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry): # load device or preset per default
        if lmenuentry != None:
            if ltopmenuname+ltopmenuentryname+lfoldername+lmenuitemname in self.action.keys():
                if self.action[ltopmenuname+ltopmenuentryname+lfoldername+lmenuitemname] != None:
                    ret = self.action[ltopmenuname+ltopmenuentryname+lfoldername+lmenuitemname](lmenuentry,lmenuentry.arg)
                    # only dummyaction return something here (their arg attribute)
                    # it can be used to control menu dynamic behavior or refresh
                    # it is used here for custom pad mapping mgmt
                    if ret != None:
                        if self._ends_with(ret[:-2],'Learn User') and self.external_mapping != None : 
                            self._active_learning_pad = int(ret[-2:])
                        elif self._ends_with(ret[:-1],'Activate Bank') and self.external_mapping != None : 
                            self.external_mapping.activate_bank(int(ret[-1:]))  
                    
        elif ltopmenuentry != None:
            if ltopmenuname+ltopmenuentryname in self.action.keys():
                if self.action[ltopmenuname+ltopmenuentryname] != None:
                    ret = self.action[ltopmenuname+ltopmenuentryname](ltopmenuentry,ltopmenuentry.arg)
                    # only dummyaction return something here (their arg attribute)
                    # it can be used to control menu dynamic behavior or refresh
                    # it is used here for custom pad mapping mgmt                   
                    if ret != None:
                        if self._ends_with(ret,'Load Mappings') and self.external_mapping != None :
                            mrs_path = ''
                            for path in sys.path:
                                if 'MIDI Remote Scripts' in path:
                                    mrs_path = path
                                    break
                            user_file = mrs_path + '/SL_Ultimate_Control_Browser/' + SETTINGS_FILE
                            #self.debug(user_file)
                            try:
                                f = open(user_file,'r')
                            except:
                                self.debug("failed to open settings file : %s" % SETTINGS_FILE)
                            self.external_mapping.load(f)
                            f.close()
                        elif self._ends_with(ret,'Save Mappings') and self.external_mapping != None :
                            mrs_path = ''
                            for path in sys.path:
                                if 'MIDI Remote Scripts' in path:
                                    mrs_path = path
                                    break
                            user_file = mrs_path + '/SL_Ultimate_Control_Browser/' + SETTINGS_FILE
                            #self.debug(user_file)
                            try:
                                f = open(user_file,'w')
                            except:
                                self.debug('error in opening file %s for saving settings' % SETTINGS_FILE)
                            self.external_mapping.save(f)
                            f.close()
                            
    def _alternate_action(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry): #remove from favorites per default
        if lmenuentry != None:
            if self.external_mapping != None and self._active_learning_pad != None :
                self.external_mapping.register_shortcuts(self._active_learning_pad,self.action[ltopmenuname+ltopmenuentryname+lfoldername+lmenuitemname].__name__,self.action[ltopmenuname+ltopmenuentryname+lfoldername+lmenuitemname],lmenuentry)
                self._active_learning_pad = None
        elif ltopmenuentry != None:
            if self.external_mapping != None and self._active_learning_pad != None :
                self.external_mapping.register_shortcuts(self._active_learning_pad,self.action[ltopmenuname+ltopmenuentryname].__name__,self.action[ltopmenuname+ltopmenuentryname],ltopmenuentry)
                self._active_learning_pad = None
    def _rebuild_menu(self):    
        topmenu = 'Track Management'
        topmenuitem = 'Set Input Device'
        self.remove_item(topmenu,topmenuitem,'','')
        self._create_io_action(True,topmenu,topmenuitem,'Input Routings','Input Sub Routings')
        topmenuitem = 'Set Output Device'
        self.remove_item(topmenu,topmenuitem,'','')
        self._create_io_action(False,topmenu,topmenuitem,'Output Routings','Output Sub Routings')
    
    def _create_tempo_action(self):
        topmenu = 'Song Settings'
        topmenuitem = 'Tempo'
        fold = 'Set Value'
        for beat in range(71,199):
            action = GlobalActions(beat,self.parent)
            menuentry=str('%03d' % beat)
            func=GlobalActions.Set_Tempo
            self.action[topmenu+topmenuitem+fold+menuentry]=func
            self.add_item(topmenu,topmenuitem,self,fold,menuentry,action)            
            self.register_main_callback(self._main_action,topmenu,topmenuitem,fold,menuentry) 

               
    def _create_quantize_action(self):
        topmenu = 'Song Settings'
        topmenuitem = 'Global Quantization'
        fold = 'Set Value'        
        for gq in GlobalActions.GQ_STATES.keys():
            action = GlobalActions(GlobalActions.GQ_STATES[gq],self.parent)
            menuentry=gq
            func=GlobalActions.Set_Global_Quantization
            self.action[topmenu+topmenuitem+fold+menuentry]=func
            self.add_item(topmenu,topmenuitem,self,fold,menuentry,action)            
            self.register_main_callback(self._main_action,topmenu,topmenuitem,fold,menuentry) 
            
    def _create_record_quantize_action(self):
        topmenu = 'Song Settings'
        topmenuitem = 'Record Quantization'
        fold = 'Set Value'      
        for rq in GlobalActions.RQ_STATES.keys():
            action = GlobalActions(GlobalActions.RQ_STATES[rq],self.parent)
            menuentry=rq
            func=GlobalActions.Set_Record_Quantization
            self.action[topmenu+topmenuitem+fold+menuentry]=func
            self.add_item(topmenu,topmenuitem,self,fold,menuentry,action)            
            self.register_main_callback(self._main_action,topmenu,topmenuitem,fold,menuentry)
            
            
    def _create_io_action(self,is_input,topmenu,topmenuitem,io_cat,io_sub_cat):
        for name in TrackActions().Get_Available_Routings(io_cat):            
            fold = 'Set Channels'
            if is_input:
                func = TrackActions.Adjust_Input_Routing
            else:
                func = TrackActions.Adjust_Output_Routing
            action = TrackActions(name,self.parent)
            self.action[topmenu+topmenuitem+''+name]=func
            self.add_item(topmenu,topmenuitem,self,'',name,action)            
            self.register_main_callback(self._main_action,topmenu,topmenuitem,'',name)            
            for sname in TrackActions().Get_Available_Routings(io_sub_cat):
                if is_input:
                    func = TrackActions.Adjust_Input_Sub_Routing
                else:
                    func = TrackActions.Adjust_Output_Sub_Routing
                action = TrackActions(sname,self.parent)
                self.action[topmenu+topmenuitem+fold+sname]=func
                self.add_item(topmenu,topmenuitem,self,fold,sname,action)
                self.register_main_callback(self._main_action,topmenu,topmenuitem,fold,sname)            
    
    def create_shortcuts(self):
        topmenu = 'Shortcuts'
        topmenuitem = 'Learn'
        for bank in range(8):
            fold = 'Bank ' + '%1d' % bank
            for pad in range(1,7):
                action = DummyActions('Learn User%01d%01d'% (bank,pad))
                menuentry=str('Learn User%01d' % pad)
                func=DummyActions.dummy_action
                self.action[topmenu+topmenuitem+fold+menuentry]=func
                self.add_item(topmenu,topmenuitem,self,fold,menuentry,action)            
                self.register_main_callback(self._main_action,topmenu,topmenuitem,fold,menuentry) 
                topmenuitem = 'Learn'
        topmenuitem = 'Activate'
        fold=''
        for bank in range(8): 
                action = DummyActions('Activate Bank%01d' % bank)
                menuentry=str('Bank %01d' % bank)
                func=DummyActions.dummy_action
                self.action[topmenu+topmenuitem+fold+menuentry]=func
                self.add_item(topmenu,topmenuitem,self,fold,menuentry,action)            
                self.register_main_callback(self._main_action,topmenu,topmenuitem,fold,menuentry)    
                
    def _create_global_browser(self):
        dummy = DummyActions(None),DummyActions.dummy_action
        global_actions = { 
            'Track Management' : {
                'New Track' : {
                    'ACTION': (dummy),
                    'ITEMS' : {
                        'New Midi Track':(TrackActions(('',MIDI1_TRACK_COLOR)), TrackActions.Create_and_Arm_Midi_Track),
                        'New Audio Track':(TrackActions(('',AUDIO_TRACK_COLOR)), TrackActions.Create_And_Arm_Audio_Track)
                        },
                    'FOLDERS' : {}
                    },
                'Delete Track': {
                    'ACTION': (TrackActions(''), TrackActions.Delete_Track),
                    'ITEMS' : {},
                    'FOLDERS' : {}
                    },
                'Duplicate Track': {
                    'ACTION' : (TrackActions(('',MIDI1_TRACK_COLOR)), TrackActions.Duplicate_Track),
                    'ITEMS' : {},
                    'FOLDERS' : {}                
                    }

                },
            'Scene Management' : {
                'New Scene' : {
                    'ACTION': (dummy),
                    'ITEMS' : {
                        'Create':(SceneActions('',parent=self.parent), SceneActions.Create_Scene),
                        'Capture':(SceneActions(0,parent=self.parent), SceneActions.Capture_Scene),
                        'Duplicate':(SceneActions('',parent=self.parent), SceneActions.Duplicate_Scene),
                        },
                    'FOLDERS' : {}    
                    },
               'Delete Scene': {
                    'ACTION': (SceneActions(''), SceneActions.Delete_Scene),
                    'ITEMS' : {},
                    'FOLDERS' : {}
                    },
            },
            'Song Settings' : {
                'Tempo' : {
                    'ACTION': (dummy),
                    'ITEMS' : {
                        'Increase Current Value':(GlobalActions(1,parent=self.parent), GlobalActions.Adjust_Tempo),
                        'Decrease Current Value':(GlobalActions(-1,parent=self.parent), GlobalActions.Adjust_Tempo),
                        },
                    'FOLDERS' : {}    
                    },
                'Global Quantization' : {
                    'ACTION': (dummy),
                    'ITEMS' : {
                        'Increase Current Value':(GlobalActions(1,parent=self.parent), GlobalActions.Adjust_Global_Quantization),
                        'Decrease Current Value':(GlobalActions(-1,parent=self.parent), GlobalActions.Adjust_Global_Quantization),
                        },
                    'FOLDERS' : {}    
                    },
                'Record Quantization' : {
                    'ACTION': (dummy),
                    'ITEMS' : {
                        'Increase Current Value':(GlobalActions(1,parent=self.parent), GlobalActions.Adjust_Record_Quantization),
                        'Decrease Current Value':(GlobalActions(-1,parent=self.parent), GlobalActions.Adjust_Record_Quantization),
                        },
                    'FOLDERS' : {}    
                    },                      
            },
            'Arrangement' : {
                'Loop' : {
                    'ACTION': (dummy),
                    'ITEMS' : {
                        'Set Loop In Marker':(GlobalActions('',parent=self.parent), GlobalActions.Set_Loop_In),
                        'Set Loop Out Marker':(GlobalActions('',parent=self.parent), GlobalActions.Set_Loop_Out),
                        },
                    'FOLDERS' : {}    
                    },   
            },
            'Shortcuts' : {
                'Reload' : {
                    'ACTION' : (DummyActions('Load Mappings'),DummyActions.dummy_action),
                    'ITEMS' : {},
                    'FOLDERS' : {}    
                    },  
                'Save' : {
                    'ACTION' : (DummyActions('Save Mappings'),DummyActions.dummy_action),
                    'ITEMS' : {},
                    'FOLDERS' : {}    
                    }, 
            },
            'Clip Management' : {
                'Delete' : {
                    'ACTION' : (ClipActions(''),ClipActions.Delete_Clip),
                    'ITEMS' : {},
                    'FOLDERS' : {}    
                    },
                'Duplicate' : {
                    'ACTION' : (ClipActions(False),ClipActions.Duplicate_Clip),
                    'ITEMS' : {},
                    'FOLDERS' : {}    
                    },  
                'Chop 8' : {
                    'ACTION' : (ClipActions(8),ClipActions.Chop_Clip),
                    'ITEMS' : {},
                    'FOLDERS' : {}    
                    }, 
                'Chop 4' : {
                    'ACTION' : (ClipActions(4),ClipActions.Chop_Clip),
                    'ITEMS' : {},
                    'FOLDERS' : {}    
                    },                      
            }            
        }
        
        for topmenu in global_actions.keys():
            for topmenuitem in global_actions[topmenu].keys():
                self.add_item(topmenu,topmenuitem,global_actions[topmenu][topmenuitem]['ACTION'][0],'','',None)
                self.action[topmenu+topmenuitem]=global_actions[topmenu][topmenuitem]['ACTION'][1]
                self.register_main_callback(self._main_action,topmenu,topmenuitem,'','')
                self.register_alternate_callback(self._alternate_action,topmenu,topmenuitem,'','')
                for menuentry in global_actions[topmenu][topmenuitem]['ITEMS'].keys():
                    self.add_item(topmenu,topmenuitem,global_actions[topmenu][topmenuitem]['ACTION'][0],'',menuentry,global_actions[topmenu][topmenuitem]['ITEMS'][menuentry][0])
                    self.action[topmenu+topmenuitem+''+menuentry]=global_actions[topmenu][topmenuitem]['ITEMS'][menuentry][1]
                    self.register_main_callback(self._main_action,topmenu,topmenuitem,'',menuentry)
                    self.register_alternate_callback(self._alternate_action,topmenu,topmenuitem,'',menuentry)
                for menufolder in global_actions[topmenu][topmenuitem]['FOLDERS'].keys():
                    self.add_item(topmenu,topmenuitem,global_actions[topmenu][topmenuitem]['ACTION'][0],menufolder,'',None)
                    for folderentry in global_actions[topmenu][topmenuitem]['FOLDERS'][menufolder].keys():
                        self.add_item(topmenu,topmenuitem,global_actions[topmenu][topmenuitem]['ACTION'][0],menufolder,folderentry,global_actions[topmenu][topmenuitem]['FOLDERS'][menufolder][folderentry][0])
                        self.action[topmenu+topmenuitem+menufolder+folderentry]=global_actions[topmenu][topmenuitem]['FOLDERS'][menufolder][folderentry][1]
                        self.register_main_callback(self._main_action,topmenu,topmenuitem,menufolder,folderentry)
                        self.register_alternate_callback(self._alternate_action,topmenu,menufolder,folderentry)

#sample_menuaction = SLMenuWithActions(global_main_action=SLOptionsMenu._builtin_test_message)
#sample_menuaction = SLOptionsMenu(None)
#print(str(sample_menuaction._browser))
#print(str(sample_menuaction._browser_action))