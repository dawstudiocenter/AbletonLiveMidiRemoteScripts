from SLMenus import SLMenuWithActions
from SLLiveActions import BrowserActions


class SLLiveCoreLibMenu(SLMenuWithActions): 
    
    SUPPORTED_TAGS = ('Drums', 'Instruments', 'Audio Effects', 'MIDI Effects', 'Max for Live', 'Samples', 'Clips')    
    
    def __init__(self,tagfilter='',devicefilter='',auto_refresh_folder_prefix='',parent=None):
        SLMenuWithActions.__init__(self,global_main_action=self._main_action,global_alternate_action=self._alternate_action,parent=parent)
        self._tagfilter = tagfilter
        self._devicefilter = devicefilter
        self._auto_refresh_folder_prefix = auto_refresh_folder_prefix
        self._create_live_browser_tags(self._tagfilter,self._devicefilter)
    def get_folditems_names_for_folder(self, ltopmenuname,ltopmenuentryname,lfoldername):   
        if self._auto_refresh_folder_prefix !='' and self._starts_with(lfoldername,self._auto_refresh_folder_prefix) :    
            self.remove_item(ltopmenuname,ltopmenuentryname,lfoldername,'')
            device = self.get_topmenuentry_from_name(ltopmenuname,ltopmenuentryname)
            folder = None
            for child in device.children:
                if lfoldername == child.name and child.is_folder :
                    folder = child
                    break
            for child in folder.children:
                if child.is_loadable and not child.name == 'Drum Rack' :
                    self.add_item(ltopmenuname,ltopmenuentryname,device,lfoldername,child.name,child)
        return SLMenuWithActions.get_folditems_names_for_folder(self, ltopmenuname,ltopmenuentryname,lfoldername)

    def _create_live_browser_tags(self,tagfilter,devicefilter):
        """ Returns the list of browser tags. 
        Also, initializes browser if it hasn't already been initialized. """
        if not self._browser:            
            for tag in BrowserActions().tags():
                if tagfilter==tag.name or (tagfilter == '' and tag.name in SLLiveCoreLibMenu.SUPPORTED_TAGS):
                    self.add_item(tag.name,'',None,'','',None)
                    self._create_devices_for_tag(tag,devicefilter)        
        
    def _create_devices_for_tag(self, tag,devicefilter):
        """ Creates dict of devices for the given tag. Special handling is needed for M4L tag, which only contains folders, and Drums tag, which contains devices and folders. """
        device_dict = {}
        if tag.name == 'Max for Live':
            for child in tag.children:
                if child.is_folder:
                    for device in child.children:
                        if device.is_device:
                            if  devicefilter=='' or (devicefilter != '' and device.name == devicefilter):
                                self.add_item(tag.name,child.name,device,'','',None)
                                self._create_items_for_device(tag,child.name,device,child)                            
                            break
        elif tag.name == 'Plug-ins':
            for child in tag.children:
                if child.is_folder:
                    for device in child.children:
                        if device.is_device or device.is_loadable:
                            if  devicefilter=='' or (devicefilter != '' and device.name == devicefilter):
                                self.add_item(tag.name,child.name,device,'','',None)
                                self._create_items_for_device(tag,child.name,device,child)                            
                            break
                else:
                    if  devicefilter=='' or (devicefilter != '' and child.name == devicefilter):
                        self.add_item(tag.name,'Others',child,'','',None)
                        self._create_items_for_device(tag,'Others',child,tag)

                    break;
        elif tag.name == 'Samples' or tag.name == 'Clips':
            for child in tag.children:
                if child.is_loadable:
                    if self._ends_with(child.name,'.wav') or self._ends_with(child.name,'.aif'):
                        try:
                            audioclip = child.name.split('_',1)
                            type = audioclip[0]
                            if type in ('LOOP','SHOT'):
                                audioclip = audioclip[1].split('_',1)
                                cat = audioclip[0]
                                if (type == 'LOOP' and cat in ('DRUMS','BASS','GUITAR','MULTI','SYNTH','VOCAL')) or (type == 'SHOT' and cat in ('BASS','SYNTH','FX','KICK','PERCUSSION','SONG','VOCAL')):
                                    audioclip = audioclip[1].split('_',1)
                                    collection = audioclip[0]
                                    bpm = 'XXXBPM'
                                    if type == 'LOOP' :
                                        audioclip = audioclip[1].split('_',1)
                                        bpm = audioclip[0]
                                    name = audioclip[1][1:-5] + audioclip[1][-4:]
                                    if type == 'LOOP' :
                                        folder = type + ' ' + cat + ' (' + bpm[0:3] + 'BPM)'
                                    elif type == 'SHOT' :
                                        folder = type + ' ' + cat
                                    else:
                                        folder = ''
                                    device = child
                                    device_name = collection
                                    preset_name = name
                                    #self._debug('%s : %s : %s : %s' % (tag.name,device_name,folder,preset_name))
                                else:
                                    device_name = 'AudioClip-'+child.name[0]
                                    device = child
                                    folder = ''
                                    preset_name = child.name
                            else:
                                device_name = 'AudioClip-'+child.name[0]
                                device = child
                                folder = ''
                                preset_name = child.name        
                        except:
                            device_name = 'AudioClip-'+child.name[0]
                            device = child
                            folder = ''
                            preset_name = child.name                               
                        self.add_item(tag.name,device_name,device,folder,preset_name,child)
                    if self._ends_with(child.name,'.alc'):
                        self.add_item(tag.name,'AbletonClip-'+child.name[0],child,'',child.name,child)
        else:
            for child in tag.children:
                if child.is_device:
                    if tag.name == 'Drums':
                        if  devicefilter=='' or (devicefilter != '' and child.name == devicefilter):
                            self.add_item(tag.name,child.name,child,'','',None)
                            self._create_items_for_device(tag,child.name,child,tag)
                    else:
                        if  devicefilter=='' or (devicefilter != '' and child.name == devicefilter):
                            self.add_item(tag.name,child.name,child,'','',None)
                            self._create_items_for_device(tag,child.name,child,child)
                            self._create_folders_for_device(tag,child.name,child,child)
                            
                elif child.is_folder and child.name =='Drum Hits':                        
                        for perc in child.children:
                            if  devicefilter=='' or (devicefilter != '' and child.name == devicefilter):
                                self.add_item(tag.name,child.name,child,perc.name,'',None)
                                self._create_items_for_folder(tag,child.name,child,perc)
                        
    def _create_items_for_device(self, tag,device_holder_name,device_holder, device):
        """ Creates dict of loadable items for the given device or folder. """
        for child in device.children:
            if child.is_loadable and not child.name == 'Drum Rack' :
                self.add_item(tag.name,device_holder_name,device_holder,'',child.name,child)
        
    def _create_items_for_folder(self, tag,device_holder_name,device_holder, device):
        """ Creates dict of loadable items for the given device or folder. """
        for child in device.children:
            if child.is_loadable and not child.name == 'Drum Rack':
                self.add_item(tag.name,device_holder_name,device_holder,device.name,child.name,child)
   
    
    def _create_folders_for_device(self,tag,device_holder_name,device_holder, device):
        """ Creates dict of folders for the given device. """
        folders_dict = {}
        for child in device.children:
            if child.is_folder:
                self.add_item(tag.name,device_holder_name,device_holder,child.name,'',None)
                self._create_items_for_folder(tag,device_holder_name,device_holder,child)

    
    def _main_action(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry): # load device or preset per default
        if lmenuentry != None:
            BrowserActions().load(lmenuentry)
        elif ltopmenuentry != None:
            BrowserActions().load(ltopmenuentry)
    
    def _alternate_action(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry): # no action per default
        pass
    
class SLLiveHotswapPresetsMenu(SLLiveCoreLibMenu): 
    def __init__(self,tagfilter='',devicefilter='',parent=None):
        SLLiveCoreLibMenu.__init__(self,tagfilter,devicefilter,'',parent)
        
class SLFavoriteLivePresetsMenu(SLMenuWithActions): 
    def __init__(self,CoreLib,parent=None):
        SLMenuWithActions.__init__(self,parent=parent)
        self.corelib=CoreLib
    def add_item_to_favorites_list(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry):
        self.add_item(ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry)
        self.register_main_callback(self.corelib._main_action,ltopmenuname,ltopmenuentryname,lfoldername,lmenuitemname)
        self.register_alternate_callback(self._alternate_action,ltopmenuname,ltopmenuentryname,lfoldername,lmenuitemname)

    def remove_item_from_favorites_list(self,ltopmenuname, ltopmenuentryname, lfoldername,lmenuitemname):
        return self.remove_item(ltopmenuname, ltopmenuentryname, lfoldername,lmenuitemname)        

    def _alternate_action(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry): #remove from favorites per default
        return self.remove_item(ltopmenuname, ltopmenuentryname, lfoldername,lmenuitemname)            
            
class SLRecentLivePresetsMenu(SLMenuWithActions):
    def __init__(self,CoreLib,FavLib,parent=None):
        SLMenuWithActions.__init__(self,parent=parent)
        self.corelib=CoreLib
        self.favlib=FavLib
    def add_item_to_recent_list(self,lbrowser, ldevicename,ldevice, lfolder,lpresetname,lpreset):
        self.add_item(lbrowser, ldevicename,ldevice,lfolder,lpresetname,lpreset)  
        self.register_main_callback(self.corelib._main_action,lbrowser,ldevicename,lfolder,lpresetname)
        self.register_alternate_callback(self._alternate_action,lbrowser,ldevicename,lfolder,lpresetname)
    def remove_item_from_recent_list(self,lbrowser, ldevicename, lfolder,lpresetname):
        return self.remove_item(lbrowser, ldevicename, lfolder,lpresetname)    

    def _alternate_action(self,ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry): #remove from favorites per default
        self.favlib.add_item_to_favorites_list(ltopmenuname, ltopmenuentryname, ltopmenuentry,lfoldername, lmenuitemname,lmenuentry)
        

