# Programmable-Attenuator-AMISR-14
Library and script for  RCDAT 8000-30
Running experiments with an external programmable attenuator in AMISR-14 using RCDAT 8000-30

* python 3:
	Just use crontab to launch attenuator.sh, the parameters have the following pattern:
	xterm -e /usr/bin/python3.x /home/{user}/pathToscript/attenuate_radar.py



* python 2: (tested 2.5.4 and 2.7.1)
	Task scheduler is needed, the python script is launched from a bat file. All the files are in the python2 folder.
	The bat file must include the route of python.exe, the path of attenuate_radar2.py and the location of the log file.
	example bat file:
	C:\path2Python\python "C:\path2script\attenuate_radar2.py" >> "C:\path2Log\logATT.txt"
	exit

The configuration of the Task scheduler on Windows:
 - Go to: Start >> All Programs >> Accessories >> System Tools >> Scheduled Tasks
 - Start a new task, configure the hour and time normaly, the user must be set as "NT AUTHORITY\SYSTEM"
