import subprocess

DETACHED_PROCESS = 0x00000008

def winjoy():
   subprocess.Popen(['control.exe', 'joy.cpl'], creationflags = DETACHED_PROCESS)
   return
   
def vJoyMonitor():
   subprocess.Popen(['c:\\Program Files\\vjoy\\JoyMonitor.exe'], creationflags = DETACHED_PROCESS)
   return

def vJoyConf():
   subprocess.Popen(['c:\\Program Files\\vjoy\\vJoyConf.exe'], creationflags = DETACHED_PROCESS)
   return
