from __future__ import with_statement

from _Framework.ControlSurface import ControlSurface
from SLBrowser import SLBrowser

class SLBrowserControl(ControlSurface):
    __doc__ = " SLBrowserControl "

    #_extra_device_count = 0
    _device = None
	
    #def _register_device():
        #SLExtraDeviceControl._extra_device_count += 1
    #_register_device = staticmethod(_register_device)

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        #self.set_suppress_rebuild_requests(True)
        with self.component_guard():
            self._device_selection_follows_track_selection = True
            self.log_message((' '+'create browser'+' ').center(50,'='))
            self._setup_device_control()
        #self.set_suppress_rebuild_requests(False)
        return None

    def disconnect(self):
        self._device = None
        ControlSurface.disconnect(self)
        SLBrowserControl._device = None
        return None

    def _setup_device_control(self,):
        if SLBrowserControl._device == None:
            SLBrowserControl._device = SLBrowser(self)
            self.set_device_component(SLBrowserControl._device)
            #self._register_device()            
        #return None
        #if SLExtraDeviceControl._extra_device_count == 0:
            #SLExtraDeviceControl._device = SLExtraDevice()
            #self.set_device_component(SLExtraDeviceControl._device)
            #self._register_device()
        return None
    def set_action_controls(self,controls):
        if SLBrowserControl._device != None:
            return SLBrowser.set_action_controls(SLBrowserControl._device,controls)