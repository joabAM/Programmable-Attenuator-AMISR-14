# Python module for Mini Circuits RCDAT-8000-30
# @date :  August, 2022
# @autor:   Joab Apaza
# @email:   roj-op01@igp.gob.pe, joab.apaza32@gmail.com

#import urllib.request as req
import urllib2 as req
import numpy as np
import time

import pip
from tabulate import tabulate

class Attenuator:


    """
    A class used to control RCDAT attenuator



    Attributes
    ----------
    says_str : str
        a formatted string to print out what the animal says

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes

    Telnet -> not implemented
    """
    def __init__(self):

        self.att_rangeList = np.arange(0,30.25,0.25)
        self.min_att = 0.0
        self.max_att = 30.0
        self.pwd_enabled = False
        self.ip = '169.254.10.10'
        self.port = 80
        self.password = None

    def show_info(self):

        list = [['Model',self.get_model()], ['Serial', self.get_serial()],['Firmware', self.get_firmware()], ['USB ADDR', self.get_usbAddr()],
                ['Ip ', self.get_ip()], ['Mask ', self.get_mask()], ['Gateway', self.get_gate()],
                ['Current Att', self.get_att()], ['StartUp Att', self.get_startUp_att()]]

        print tabulate(list, headers=['Parameter', 'Value'])

    ##--------------------------------------------------------------------------
    def get(self, command):

        if self.pwd_enabled:
            pwd = self.password
        else:
            pwd = ''
        s = "http://%s:%s/PWD=%s%s" %(self.ip, self.port, pwd, command)
        
        s += "?"
        #print s
        url = req.urlopen(s)
        return url.read().decode('utf-8')

    def set(self, command):
        if self.pwd_enabled:
            pwd = self.password
        else:
            pwd = ''
        s = "http://%s:%s/PWD=%s%s" %(self.ip, self.port, pwd, command)
        #print s
        url = req.urlopen(s)
        return  url.read().decode('utf-8')

    ##--------------------------------------------------------------------------
    def get_model(self):
        r = self.get(':MN')
        return r
    def get_serial(self):
        r = self.get(':SN')
        return r
    def get_usbAddr(self):
        r = self.get(':ADD')
        return r
    def get_firmware(self):
        r = self.get(':FIRMWARE')
        return r

    def set_lastAtt(self):
        r = self.set(':LASTATT:STORE:INITIATE')
        return r
    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------
    def setup(self, mode='N', ip=None, mask=None, gateway=None, port=None, usb_adr=None, password=None, on_att=30):
        r = True
        self.ip = ip
        if ip == None:
            if not self.set_DHCP(1):
                print "setting dhcp failed"
        else:
            currentIp = self.get_ip()
            if currentIp != ip:
                print "changing ip from %s to %s"%(currentIp,ip)
                if not self.set_ip(ip):
                    print "setting ip:%s failed"%(ip)
            else:
                print "Same previous IP"
        self.ip = self.get_ip()
        if port != None:
            r = self.set_portHTTP(port)
            self.port = port
        if not r:
            print "Failed setting port"
            return False

        if mask != None:
            r = self.set_mask('255.255.255.0')
        else:
            r = self.set_mask(mask)
        if not r:
            print "Failed setting mask"
            return False

        if gateway == None:
            s = ip.split('.')[:-1]
            gate = '.'.join(s) + '.1'
            r = self.set_gate(gate)
        else:
            r = self.set_gate(gateway)
        if not r:
            print "Failed setting gateway"
            return False

        if password == None:
            self.pwd_enabled = False
        else:
            r = self.set_psswdHTTP(password)
            if r == 0:
                print "Failed setting password "
            self.pwd_enabled = True
            self.password = password

        if not self.set_startUp_att(on_att):
            print "Failed setting start-up attenuation"

        if not self.update_configHTTP():
            print "Failed updating ip config...."

        self.set_startUp_mode(mode)
    ##--------------------------------------------------------------------------

    def att_ramp(self, start=None, stop=None, step=None, time_ms=None ):
        count_ok = 0
        '''ramp mode for starting or finishing experiments
        '''

        if start<0 or start>30:
            print "Error start value"
        if stop<0 or stop>30:
            print "Error stop value"
        if step % 0.25 != 0:
            print "Step must be multiple of 0.25dB"
            return
        inc = 0.25
        if step < 0.25:
            print "error, minimum resolution is 0.25dB"
        else:
            inc = int(step/0.25) * 0.25

        if stop < start: #it'll decrease over time
            inc *= -1
        atts = np.arange(start,(stop+inc),inc)
        #print atts
        for att in atts:
            self.set_att(att)
            if att != self.get_att():
                print "Error set attenuation step %f"%(att)

            time.sleep(time_ms/1000)
            '''
            target_time = time.clock() + (time_ms/1000)
            #print target_time-time.clock()
            while time.clock() < target_time:
                pass
            '''
        print "Ramp from %f dB to %f dB completed."%(atts[0], atts[-1])



    ##--------------------------------------------------------------------------
    def config_sweep(self, mode, start, stop, step, time_ms=None, time_us=None, time_s=None ):
        count_ok = 0
        '''ramp mode for starting or finishing experiments
        '''
        if stop < start:
            print "Stop value must be higher than start."
            return
        if start<0 or start>30:
            print "Error start value"
        if stop<0 or stop>30:
            print "Error stop value"

        if mode =='up':
            count_ok += self.set_directionSweep(0) #forward
        elif mode == 'down':
            count_ok += self.set_directionSweep(1) #backward
        else:
            print "Invalid mode selected, use only 'up' or 'down' "
            return

        if time_ms!=None :
            count_ok += self.set_dwellTimeUnitsSweep('M')
            count_ok +=  self.set_dwellTimeSweep(time_ms)
        elif time_us!=None :
            count_ok += self.set_dwellTimeUnitsSweep('L')
            count_ok +=  self.set_dwellTimeSweep(time_us)
        elif time_s!=None :
            count_ok += self.set_dwellTimeUnitsSweep('S')
            count_ok +=  self.set_dwellTimeSweep(time_s)
        else:
            print "Step time neccesary!"
            return
        if step % 0.25 != 0:
            print "Step must be multiple of 0.25dB"
            return
        count_ok += self.set_startAttSweep(start)
        count_ok += self.set_stopAttSweep(stop)
        count_ok += self.set_stepAttSweep(step)

    ##--------------------------------------------------------------------------
    def config_hop(self, mode, start, stop, points, time_ms=None, time_us=None, time_s=None ):
        count_ok = 0
        '''ramp mode for starting or finishing experiments
        '''
        if stop < start:
            print "Stop value must be higher than start."
            return
        if start<0 or start>30:
            print "Error start value"
        if stop<0 or stop>30:
            print "Error stop value"


        if mode =='up':
            count_ok += self.set_directionHop(0) #forward
            att = start
        elif mode == 'down':
            count_ok += self.set_directionHop(1) #backward
            att = stop
        else:
            print "Invalid mode selected, use only 'up' or 'down' "
            return


        if points < 0:
            print "Missing number of points"
            return
        else:
            count_ok += self.set_pointsHop(points)

        step = (stop - start)/points
        inc = 0
        if step < 0.25:
            print "error, minimum resolution is 0.25dB"
        else:
            inc = int(step/0.25)
        time = 0
        # if count_ok < 4:
        #     print "error config step"
        if mode == 'down':
            inc *= -1
        for n in range(points):
            count_ok += self.set_indexPointHop(n)
            if time_ms!=None :
                count_ok += self.set_dwellTimeUnitsHop('M')
                time = time_ms
            elif time_us!=None :
                count_ok += self.set_dwellTimeUnitsHop('L')
                time = time_us
            elif time_s!=None :
                count_ok += self.set_dwellTimeUnitsHop('S')
                time = time_s
            else:
                print "Step time neccesary!"
                return
            count_ok +=  self.set_dwellTimeHop(time)
            count_ok += self.set_attPointHop(att)
            att += (inc*0.25)
            #print n, att, self.get_dwellTimeHop(), self.get_attPointHop()

    ##--------------------------------------------------------------------------
    ''' ############################### NETWORK ############################'''

    def get_ip(self):
        r = self.get(':ETHERNET:CONFIG:IP')
        return r
    def set_ip(self, ip):
        r = int(self.set(':ETHERNET:CONFIG:IP:%s'%(ip)))
        return r
    ##--------------------------------------------------------------------------
    def set_mask(self, mask):
        r = self.set(':ETHERNET:CONFIG:SM:%s'%(mask))
        return int(r)
    def get_mask(self):
        r = self.get(':ETHERNET:CONFIG:SM')
        return r
    ##--------------------------------------------------------------------------
    def set_gate(self, gateway):
        r = self.set(':ETHERNET:CONFIG:NG:%s'%(gateway))
        return int(r)
    def get_gate(self):
        r = self.get(':ETHERNET:CONFIG:NG')
        return r
    ##--------------------------------------------------------------------------
    def get_portHTTP(self):
        r = self.get(':ETHERNET:CONFIG:HTPORT')
        return int(r)
    def set_portHTTP(self, port):
        r = int(self.set(':ETHERNET:CONFIG:HTPORT:%d'%(port)))
        return r
    ##--------------------------------------------------------------------------
    def set_enablePSSWD(self, flag):
        r = int(self.set(':ETHERNET:CONFIG:PWDENABLED:%r'%(flag)))
        return r
    def get_enablePSSWD(self):
        r = self.get(':ETHERNET:CONFIG:PWDENABLED')
        return int(r)
    ##--------------------------------------------------------------------------
    def set_psswdHTTP(self, password):
        r = self.set(':ETHERNET:CONFIG:PWD:%s'%(password))
        return int(r)
    def get_psswdHTTP(self):
        r = self.get(':ETHERNET:CONFIG:PWD')
        return int(r)
    ##--------------------------------------------------------------------------
    def set_DHCP(self, enable):
        r = self.set(':ETHERNET:CONFIG:DHCPENABLED:%r'%(enable))
        return int(r)
    def get_DHCP(self):
        r = self.get(':ETHERNET:CONFIG:DHCPENABLED')
        return int(r)
    ##--------------------------------------------------------------------------
    def get_MAC(self):
        r = self.get(':ETHERNET:CONFIG:MAC')
        return r

    def get_configIP(self):
        r = self.get(':ETHERNET:CONFIG:LISTEN')
        return r

    def disable_Ethernet(self):
        pass

    def update_configHTTP(self):
        r = self.set(':ETHERNET:CONFIG:INIT')
        return int(r)
    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------

    def set_att(self, value):

        r = int(self.set(':SETATT=%r'%(value)))
        if r == 0:
            print "Command failed or invalid attenuation set, use one from: "
            print self.att_rangeList
            return False
        elif r == 1:
            return True
        elif r == 2:
            print "Requested attenuation was higher than the allowed range, the attenuation was set to the devices maximum allowed value"
        return True

    def get_att(self):
        r = self.get(':ATT')
        return float(r)
    ##--------------------------------------------------------------------------
    def set_startUp_att(self, value):
        r = int(self.set(':STARTUPATT:VALUE:%f'%(value)))
        return r # 0 failed, 1 successful
    def get_startUp_att(self):
        r = self.get(':STARTUPATT:VALUE')
        return float(r)
    ##--------------------------------------------------------------------------
    def set_startUp_mode(self, value):# L=Last Value, F=Fixed Value, N=Default
        r = int(self.set(':STARTUPATT:INDICATOR:%f'%(value)))
        return r # 0 failed, 1 successful
    def get_startUp_mode(self):
        r = self.get(':STARTUPATT:INDICATOR')
        return r
    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------
    ''' ############################### Hop MODE ############################'''
    def set_pointsHop(self, points):
        r = self.set(':HOP:POINTS:%d'%(points))
        return int(r)
    def get_pointsHop(self):
        r = self.get(':HOP:POINTS')
        return int(r)
    ##--------------------------------------------------------------------------
    def set_activeChHop(self, ch):
        pass
    def get_activeChHop(self):
        pass
    ##--------------------------------------------------------------------------
    '''0->forward, 1-> backward, 2->bi-directional'''
    def set_directionHop(self, direction):
        r = self.set(':HOP:DIRECTION:%s'%(direction))
        return int(r)
    def get_directionHop(self):
        r = self.get(':HOP:DIRECTION')
        return int(r)

    ##--------------------------------------------------------------------------
    def set_indexPointHop(self, index):
        r = self.set(':HOP:POINT:%d'%(index))
        return int(r)
    def get_indexPointHop(self):
        r = self.get(':HOP:POINT')
        return int(r)

    ##--------------------------------------------------------------------------
    '''Sets the units to be used for the dwell time of the indexed point in the hop sequence.
    U -> us, M -> ms, S -> s'''
    def set_dwellTimeUnitsHop(self, units):
        r = self.set(':HOP:DWELL_UNIT:%s'%(units))
        return int(r)
    '''Sets the dwell time of the indexed point in the hop sequence. The dwell time units are defined separately.'''
    def set_dwellTimeHop(self, time):
        r = self.set(':HOP:DWELL:%d'%(time))
        return int(r)
    def get_dwellTimeHop(self):
        r = self.get(':HOP:DWELL')
        return r
    ##--------------------------------------------------------------------------
    def set_attPointHop(self, point_att):
        r = self.set(':HOP:ATT:%d'%(point_att))
        return int(r)
    def get_attPointHop(self):
        r = self.get(':HOP:ATT')
        return float(r)

    ##--------------------------------------------------------------------------
    def enableHopMode(self, enable):
        a = 'ON' if enable else  'OFF'
        r = self.set(':HOP:MODE:%s'%(a))
        return int(r)

    ##--------------------------------------------------------------------------
    ''' ############################# Sweep MODE ############################'''
    ##--------------------------------------------------------------------------
    '''0->forward, 1-> backward, 2->bi-directional'''
    def set_directionSweep(self, direction):
        r = self.set(':SWEEP:DIRECTION:%d'%(direction))
        return int(r)
    def get_directionSweep(self):
        r = self.get(':SWEEP:DIRECTION')
        return int(r)
    ##--------------------------------------------------------------------------
    '''Sets the units to be used for the sweep dwell time..
    U -> us, M -> ms, S -> s'''
    def set_dwellTimeUnitsSweep(self, units):
        r = self.set(':SWEEP:DWELL_UNIT:%s'%(units))
        return int(r)
    '''Sets the dwell time to be used for the sweep. The dwell time units are defined separately'''
    def set_dwellTimeSweep(self, time):
        r = self.set(':SWEEP:DWELL:%d'%(time))
        return int(r)
    def get_dwellTimeSweep(self):
        r = self.get(':SWEEP:DWELL')
        return r
    ##--------------------------------------------------------------------------
    def set_startAttSweep(self, start):
        r = self.set(':SWEEP:START:%r'%(start))
        return int(r)
    def get_startAttSweep(self):
        r = self.get(':SWEEP:START')
        return int(r)
    ##--------------------------------------------------------------------------
    def set_stopAttSweep(self, stop):
        r = self.set(':SWEEP:STOP:%r'%(stop))
        return int(r)
    def get_stopAttSweep(self):
        r = self.get(':SWEEP:STOP')
        return int(r)
    ##--------------------------------------------------------------------------
    def set_stepAttSweep(self, stop):
        r = self.set(':SWEEP:STEPSIZE:%r'%(stop))
        return int(r)
    def get_stepAttSweep(self):
        r = self.get(':SWEEP:STEPSIZE')
        return float(r)
    ##--------------------------------------------------------------------------
    def enableSweepMode(self, enable):
        a = 'ON' if enable else 'OFF'
        r = self.set(':SWEEP:MODE:%s'%(a))
        return int(r)


    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------
    ##--------------------------------------------------------------------------




if __name__ == '__main__':
    att = Attenuator()

    att.setup(ip='169.254.10.10', on_att=5.0)
    print att.get_configIP()
    #print(att.set_att(20))
    print att.get_att()


    # att.att_ramp( start=25, stop=2, step=1.7, time_ms=100 )
    #
    # # print "check_point")
    # print(att.get_att())
    # print(att.get_configIP())
