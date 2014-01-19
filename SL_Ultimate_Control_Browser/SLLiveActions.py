import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

               
class Actions(ControlSurfaceComponent):
    def __init(self):  
        ControlSurfaceComponent.__init__(self)
    def debug(self,msg):
        if self.parent != None:
            s = msg.encode('utf-8')
            return self.parent.log_message(s)
        
    def _get_name(self, name):
        """ Convert name to upper-case string or return blank string if couldn't be converted """
        try: name = str(name).upper()
        except: name = ''
        return name

class DummyActions():
    def __init__(self,arg=None):
        if arg != None:
            self.arg=arg 
    def dummy_action(self,arg):
        return self.arg
        
class GlobalActions(Actions):
    GQ_STATES = {'NONE' : 0, '8 BARS' : 1, '4 BARS' : 2, '2 BARS' : 3, '1 BAR' : 4, '1/2' : 5, '1/2T' : 6, '1/4' : 7, '1/4T' : 8, '1/8' : 9, '1/8T' : 10, '1/16' : 11, '1/16T' : 12, '1/32' : 13}
    RQ_STATES = {'NONE' : 0, '1/4' : 1, '1/8' : 2, '1/8T' : 3, '1/8 + 1/8T' : 4, '1/16' : 5, '1/16T' : 6, '1/16 + 1/16T' : 7, '1/32' : 8}           
    R_QNTZ_STATES = {'1/4' : Live.Song.RecordingQuantization.rec_q_quarter, '1/8' : Live.Song.RecordingQuantization.rec_q_eight, 
                   '1/8T' : Live.Song.RecordingQuantization.rec_q_eight_triplet, '1/8 + 1/8T' : Live.Song.RecordingQuantization.rec_q_eight_eight_triplet, '1/16' : Live.Song.RecordingQuantization.rec_q_sixtenth, 
                   '1/16T' : Live.Song.RecordingQuantization.rec_q_sixtenth_triplet, '1/16 + 1/16T' : Live.Song.RecordingQuantization.rec_q_sixtenth_sixtenth_triplet, 
                   '1/32' : Live.Song.RecordingQuantization.rec_q_thirtysecond}
    def __init__(self,arg=None,parent=None):
        Actions.__init__(self)
        if arg != None:
            self.arg=arg    
        if parent != None:
            self.parent = parent      
    
    def _one_measure_in_beats(self):
        return 4.0 * self.song().signature_numerator / self.song().signature_denominator

    def Set_Loop_In(self,arg):
        pass        
    def Set_Loop_Out(self,arg): 
        pass        
    def Set_Loop_Inc(self,arg):
        pass
        
    def Set_Loop_Dec(self,arg):
        pass        
        
    def Set_Tempo(self,arg):
        self.song().tempo = int(arg)
        
    def Adjust_Tempo(self, arg):
        try:
            factor=int(arg)
            self.song().tempo = max(20, min(999, (self.song().tempo + factor)))
        except:
            pass
            
    def Adjust_Global_Quantization(self, arg):
        new_gq = self.song().clip_trigger_quantization + arg
        if new_gq in range (14):
            self.song().clip_trigger_quantization = new_gq
        else:
            if self.song().clip_trigger_quantization != 0:
                self._last_gqntz = int(self.song().clip_trigger_quantization)
                self.song().clip_trigger_quantization = 0
            else:
                self.song().clip_trigger_quantization = self._last_gqntz
        
    def Adjust_Record_Quantization(self, arg):
        new_rq = self.song().midi_recording_quantization + arg
        if new_rq in range (9):
            self.song().midi_recording_quantization = new_rq
        else:
            if self.song().midi_recording_quantization != 0:
                self._last_rqntz = int(self.song().midi_recording_quantization)
                self.song().midi_recording_quantization = 0
            else:
                self.song().midi_recording_quantization = self._last_rqntz   
        
    def Set_Global_Quantization(self, arg):
        self.song().clip_trigger_quantization = arg
        
    
    def Set_Record_Quantization(self, arg):
        self.song().midi_recording_quantization = arg

        
class ClipActions(Actions):
    def __init__(self,arg=None,parent=None):
        Actions.__init__(self)
        if arg != None:
            self.arg=arg 
        if parent != None:
            self.parent = parent
    def Clear_All_Envelopes(self, arg=None):
        """ Clears all envelopes from the selected clip. """
        clip = self.song().view.highlighted_clip_slot
        clip.clear_all_envelopes()
        
class TrackActions(Actions):
    def __init__(self,arg=None,parent=None):
        Actions.__init__(self)
        if arg != None:
            self.arg=arg 
        if parent != None:
            self.parent = parent
            
    def Adjust_Input_Routing(self, arg): 
        """ Adjust track input routing """
        track = self.song().view.selected_track
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_routings)
            current_routing = 0
            if track.current_input_routing in routings: 
                current_routing = routings.index(track.current_input_routing)
                track.current_input_routing = self._handle_track_routing(arg, routings, current_routing)
            
            
    def Adjust_Input_Sub_Routing(self, arg): 
        """ Adjust track input sub-routing """
        track = self.song().view.selected_track
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_sub_routings)
            current_routing = 0
            if track.current_input_sub_routing in routings:
                current_routing = routings.index(track.current_input_sub_routing)
                track.current_input_sub_routing = self._handle_track_routing(arg, routings, current_routing)
            
            
    def Adjust_Output_Routing(self, arg): 
        """ Adjust track output routing """
        track = self.song().view.selected_track
        if track != self.song().master_track:
            routings = list(track.output_routings)
            current_routing = 0
            if track.current_output_routing in routings:
                current_routing = routings.index(track.current_output_routing)
                track.current_output_routing = self._handle_track_routing(arg, routings, current_routing)
            
            
    def Adjust_Output_Sub_Routing(self, arg): 
        """ Adjust track output sub-routing """
        track = self.song().view.selected_track
        if track != self.song().master_track:
            routings = list(track.output_sub_routings)
            current_routing = 0
            if track.current_output_sub_routing in routings:
                current_routing = routings.index(track.current_output_sub_routing)
                track.current_output_sub_routing = self._handle_track_routing(arg, routings, current_routing)

            
    def Get_Available_Routings(self, arg):
        routings = []
        track = self.song().view.selected_track
        if track != self.song().master_track:
            if arg == 'Input Routings':
                routings = list(track.input_routings)
            elif arg == 'Input Sub Routings':
                routings = list(track.input_sub_routings)
            elif arg == 'Output Routings':
                routings = list(track.output_routings)
            elif arg == 'Output Sub Routings':
                routings = list(track.output_sub_routings)
        return routings
            
    def _handle_track_routing(self, args, routings, current_routing):
        """ Handle track routing adjustment """
        new_routing = routings[current_routing]
        args = args.strip()
        for i in routings:
            if i == args: 
                new_routing = i
                break
        return new_routing
    
    def Set_Midi_Input(self,arg):        
        _input_port_name = ''
        if arg != None:
            for i in self.song().view.selected_track.input_routings:
                if str(arg) in i :
                    _input_port_name = i
        if _input_port_name != '':
            self.song().view.selected_track.current_input_routing = _input_port_name    
            
            
    def Create_and_Arm_Midi_Track(self,arg):        
        if arg != None:
            self._inputmidiportname = arg[0]
            self._color=arg[1]
        try:        
            self.song().create_midi_track(list(self.song().tracks).index(self.song().view.selected_track)+1)
            _input_port_name = ''
            for i in self.song().view.selected_track.input_routings:
                if self._inputmidiportname in i :
                    _input_port_name = i
            if _input_port_name != '':
                self.song().view.selected_track.current_input_routing = _input_port_name
            if self._color != -1:
                self.song().view.selected_track.color=int(self._color)
            self.song().view.selected_track.arm
        except:
            pass #max number of track reached or inserting track in send tracks + master track section
    def Create_And_Arm_Audio_Track(self,arg):
        if arg != None:
            self._inputaudioportname = arg[0]
            self._color=arg[1]
        try:
            self.song().create_audio_track(list(self.song().tracks).index(self.song().view.selected_track)+1)
            if self._color != -1:
                self.song().view.selected_track.color=int(self._color)
            self.song().view.selected_track.arm
        except:
            pass #max number of track reached or inserting track in send tracks + master track section
    def Duplicate_Track(self,arg):
        track = self.song().view.selected_track
        if track in self.song().tracks:
            self.song().duplicate_track(list(self.song().tracks).index(track))
            
    def Delete_Track(self,arg):
        track = self.song().view.selected_track
        if track in self.song().tracks:
            self.song().delete_track(list(self.song().tracks).index(track))

class ClipActions(Actions):
    name='Clip'
    def __init__(self,arg=None,parent=None):
        Actions.__init__(self)
        if arg != None:
            self.arg = arg
        if parent!=None:
            self.__parent=parent
    def debug(self,msg):
        if self.__parent != None:
            s = msg.encode('utf-8')
            return self.__parent.log_message(s)
    
    def Delete_Clip(self,arg):
        track = self.song().view.selected_track
        slot_idx = list(self.song().scenes).index(self.song().view.selected_scene)
        clip = track.clip_slots[slot_idx].clip    
        clip.canonical_parent.delete_clip()
        
    def Duplicate_Clip(self, arg):    
        track = self.song().view.selected_track
        slot_idx = list(self.song().scenes).index(self.song().view.selected_scene)
        clip = track.clip_slots[slot_idx].clip    
        new_slot=track.duplicate_clip_slot(list(track.clip_slots).index(clip.canonical_parent))
        self.song().view.selected_scene = self.song().scenes[new_slot]      
        if arg==True:
            track.clip_slots[new_slot].clip.fire()
        
        
    def Chop_Clip(self, arg):    
        track = self.song().view.selected_track        
        if arg != None:
            num_chops = arg
        else:
            num_chops = 8    
        #slot_idx = list(track.clip_slots).index(clip.canonical_parent)
        slot_idx = list(self.song().scenes).index(self.song().view.selected_scene)
        clip = track.clip_slots[slot_idx].clip
        current_start = clip.start_marker
        chop_length = (clip.loop_end - current_start) / num_chops
        for index in range(num_chops - 1):
            track.duplicate_clip_slot(slot_idx + index)
            dupe_start = (chop_length * (index + 1)) + current_start
            dupe = track.clip_slots[slot_idx + index + 1].clip
            dupe.start_marker = dupe_start
            dupe.loop_start = dupe_start
            dupe.name = clip.name + '-' + str(index + 1)
        
class SceneActions(Actions):
    name='Scene'
    def __init__(self,arg=None,parent=None):
        Actions.__init__(self)
        if arg != None:
            self.arg = arg
        if parent!=None:
            self.__parent=parent
    def debug(self,msg):
        if self.__parent != None:
            s = msg.encode('utf-8')
            return self.__parent.log_message(s)
            
    def Capture_Scene(self,arg):        
        try:
            scene = list(self.song().scenes).index(self.song().view.selected_scene)            
            #self.song().view.selected_scene = list(self.song().scenes).index(self.song().view.selected_scene)
            #self.debug('%s %s' % (str(scene),str(self.song().view.selected_scene)))
            self.song().view.selected_scene = self.song().scenes[scene+int(arg)]
            self.song().capture_and_insert_scene()
        except:
            pass    
    def Duplicate_Scene(self,arg): 
        scene = list(self.song().scenes).index(self.song().view.selected_scene) 
        self.song().duplicate_scene(scene)

    def Delete_Scene(self,arg):
        scene = list(self.song().scenes).index(self.song().view.selected_scene)
        if len(self.song().scenes) > 1:
            self.song().delete_scene(scene)
            
    def Create_Scene(self, arg):
        scene = list(self.song().scenes).index(self.song().view.selected_scene)
        self.song().create_scene(scene)
            
class BrowserActions(Actions):
    name='Browser'
    def __init__(self,arg=None,parent=None):
        Actions.__init__(self)
        if arg != None:
            self.arg = arg
        if parent != None:
            self.parent = parent
    def places(self):
        return Live.Application.get_application().browser.places
    def tags(self):
        return Live.Application.get_application().browser.tags   
   
    
    def get_filter_for_device(self,arg=None):
        tag_to_use = ''
        device_to_use = ''        
        device = self.song().view.selected_track.view.selected_device
        # self.debug(' Hotswap : %s' % str(Live.Application.get_application().browser.filter_type))
        # self.debug(' Have Chains %s, have drum pads : %s, selected device : %s' % (device.can_have_chains,device.has_drum_pads,device.name))
        # if device.can_have_chains and device.has_drum_pads and device.view.selected_chain != None:
            # device = device.view.selected_chain.devices[0]
            # self.debug(' retained instrument : %s' % device.name)
        
        if device != None:
            if device.class_name != 'PluginDevice': #non hotswap
                device_to_use = device.class_display_name
                if device.can_have_drum_pads:
                    tag_to_use = 'Drums'
                elif device.class_display_name.startswith('Max'):
                    tag_to_use = 'Max for Live'
                elif device.type == Live.Device.DeviceType.audio_effect:
                    tag_to_use = 'Audio Effects'
                elif device.type == Live.Device.DeviceType.midi_effect:
                    tag_to_use = 'MIDI Effects'
                elif device.type == Live.Device.DeviceType.instrument:
                    tag_to_use = 'Instruments'
        #self.debug('hotswap target : %s : %s' % (tag_to_use,device_to_use))
        return (tag_to_use,device_to_use)
        
    def load(self,arg):
        if arg != None:
            Live.Application.get_application().browser.load_item(arg)

    def Insert_Clip(self,arg):
        if arg != None:
            previous_track = self.song().view.selected_track
            previous_scene_idx = list(self.song().scenes).index(self.song().view.selected_scene) 
            previous_clip = previous_track.clip_slots[previous_scene_idx].clip
            if previous_clip != None:
                self.debug('not empty')
            else:
                self.debug('empty')
                Live.Application.get_application().browser.load_item(arg)
                current_track = self.song().view.selected_track
                current_scene_idx = list(self.song().scenes).index(self.song().view.selected_scene) 
                current_clip = current_track.clip_slots[current_scene_idx].clip 
                if previous_clip != current_clip:          
                    previous_clip = current_clip
                    #self.song().delete_track(list(self.song().tracks).index(current_track))
                #Live.Application.get_application().browser.load_item(arg)
