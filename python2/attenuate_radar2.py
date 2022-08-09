
#import sys
#import os
#cwd = os.getcwd()
# insert at 1, 0 is the script path (or '' in REPL)
#sys.path.insert(1, cwd)

from ATT_RCDAT2 import Attenuator

from time import sleep

################################################################################

ip = '192.168.10.27'
##ip = '169.254.10.10'
mask = '255.255.255.0'
gateway = '10.10.40.1'
startUp_attenuation = 30

ramp_time = 60 # seconds
steady_time = 1  # minutes
startUpMode = 'F'  # L=Last Value, F=Fixed Value, N=Default
minAtt = 0
maxAtt = 30

################################################################################
if minAtt%0.25 != 0.0:
    print "Error min attenuation value"
if maxAtt%0.25 != 0.0:
    print "Error max attenuation value"

att = Attenuator()
# try:
#     att.show_info()
# except:
#     print "No setup")
att.setup(ip=ip, mask=mask, on_att=startUp_attenuation, mode=startUpMode )#, gateway=gateway)
print "---------------------------------------"
att.show_info()

steps = (maxAtt-minAtt)/0.25
steptime = int((ramp_time*1000)/steps)
att_time = (steady_time*60)
print "---------------------------------------"
print "Ramp time: %2.2f s"%(ramp_time)
print "Steady time: %2.2f s"%(att_time)
print "Step Time: %2.2f ms"%(steptime)
print "Steps: ", steps
print "---------------------------------------"
print "starting attenuetion"
print "---------------------------------------"
att.att_ramp( start=minAtt, stop=maxAtt, step=0.25, time_ms=steptime )
print "---------------------------------------"
print "starting steady time"
sleep(att_time)
print "steady time finished"
print "---------------------------------------"
att.att_ramp( start=maxAtt, stop=minAtt, step=0.25, time_ms=steptime )

#att.set_att(minAtt)
att.set_lastAtt()
print "---------------------------------------"
print "Current Attenuation: %2.2f dB"%(att.get_att())
print " "
print "Radar attenuator completed :)"
sleep(30)
