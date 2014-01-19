from __future__ import with_statement

from _Framework.ControlSurface import ControlSurface
from SLExtraDevice import SLExtraDevice

class SLExtraDeviceControl(ControlSurface):
    __doc__ = " SLExtraDevice "

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
            self._setup_device_control()
        #self.set_suppress_rebuild_requests(False)
        return None

    def disconnect(self):
        self._device = None
        ControlSurface.disconnect(self)
        SLExtraDeviceControl._device = None
        return None

    def _setup_device_control(self):
        if SLExtraDeviceControl._device == None:
            SLExtraDeviceControl._device = SLExtraDevice()
            self.set_device_component(SLExtraDeviceControl._device)
            #self._register_device()            
        #return None
        #if SLExtraDeviceControl._extra_device_count == 0:
            #SLExtraDeviceControl._device = SLExtraDevice()
            #self.set_device_component(SLExtraDeviceControl._device)
            #self._register_device()
        return None
