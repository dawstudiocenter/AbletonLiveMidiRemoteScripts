from SLLiveActions import *

class SLPadMapping():
    def __init__(self,parent=None):
        self.shortcuts = {}
        self.parent=parent
        self.bank_id = 0        
    def register_shortcuts(self,id,name,action,instance): #id is an int (XY, X represent the bank, Y represent the control id), name is the action name, action is the class method to register, instance is the class object with an arg attribute that provide the action method
        idstr=str('%02d' % id)
        bank_id=int(idstr[len(idstr)-2])
        ctl_id = int(idstr[len(idstr)-1])
        #self.parent.debug('%02d - register bank : %01d, pad : %01d' % (id,bank_id,ctl_id) + ' Action Name : %s' % name + ' Instance : %s' % str(instance) + ' Arg : %s' %str(instance.arg) )
        newmapping = {ctl_id:{'name':name,'action':action,'instance':instance}  }
        if bank_id in self.shortcuts.keys():
            self.shortcuts[bank_id] = dict(self.shortcuts[bank_id].items() + newmapping.items())
        else:
            self.shortcuts[bank_id] = newmapping
    def get_bank_action_names(self,id):
        strings = []
        strings.append('BANK%01d'%id)
        if id in self.shortcuts.keys():
            for mapid in range(1,7):
                if mapid in self.shortcuts[id].keys():
                    strings.append(self.shortcuts[self.bank_id][mapid]['name'])
                else:
                    strings[mapid].append('NONE')
        return strings
    def activate_bank(self,id):
        #self.parent.debug('bank activated: %02d' % id)
        self.bank_id = id
    def call(self,id):
        #self.parent.debug('calling: %02d' % id)
        if self.bank_id in self.shortcuts.keys():
            if id in self.shortcuts[self.bank_id].keys():
                if self.shortcuts[self.bank_id][id]['action'] != None:
                    self.shortcuts[self.bank_id][id]['action'](self.shortcuts[self.bank_id][id]['instance'],self.shortcuts[self.bank_id][id]['instance'].arg)
    
    def save(self,arg): #arg is an opened file
        if arg != None:
            if self.shortcuts != {}:            
                for bank in self.shortcuts.keys():
                    for mapid in self.shortcuts[bank].keys():
                        arg.write('<MAPPING>\n')
                        arg.write('<BANK>%1d</BANK>\n' % bank)                
                        arg.write('<NAME>%1d</NAME>\n' % mapid)
                        arg.write('<ACTION>%s</ACTION>\n' % self.shortcuts[bank][mapid]['name'])
                        arg.write('<OBJECTS>%s,%s</OBJECTS>\n' % (self.shortcuts[bank][mapid]['instance'].__class__.__name__,repr(self.shortcuts[bank][mapid]['instance'].arg)))
                        arg.write('</MAPPING>\n')        
    
    def load(self,arg): #arg is an opened file
        lines = [line.strip() for line in arg]
        step = 0
        lbank = ''
        lname = ''
        laction = ''
        lclass = ''
        larg = ''
        skip=False
        for line in lines:            
            if step == 0:
                if line[1:8]=='MAPPING':                    
                    skip=False
                else:
                    skip=True
            else:
                if not(skip):
                    if step == 1:
                        #self.debug(line[6:-7])
                        lbank = int(line[6:-7])
                    elif step == 2:
                        #self.debug(line[8:-9])
                        lname = int(line[6:-7])
                        #self.debug('-> %s' % ldevice)
                    elif step == 3:
                        #self.debug(line[8:-9])
                        laction = line[8:-9]
                    elif step == 4:
                        lclass, larg = line[9:-10].split(',',1)
                    elif step == 5:                        
                        constructor = globals()[lclass]                        
                        if larg != '':
                            arg = eval(larg)
                        else:
                            arg=''
                        #self.debug(larg + '->' + str(arg))
                        instance = constructor(arg)
                        action=getattr(instance.__class__,laction)
                        self.register_shortcuts(int('%01d%01d' % (lbank,lname)),laction,action,instance)
                    else:
                        raise AssertionError
            step = (step +1)%6