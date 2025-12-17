'''Definition of a test apparatus, running a liteServer with peak simulator.
The managers for this example could be installed with pip:
  pip install liteserver pvplot pypeto

The script should define dictionary startup.
Supported keys are:
  'cmd': command which will be used to start and stop the manager,
  'cd:   directory (if needed), from where to run the cmd,
  'process': used for stopping the manager using 'pkill -f', if cmd properly identifies the 
     manager, then this key is not necessary,
  'help': it will be used as a tooltip,
'''
import os
homeDir = os.environ['HOME']
epics_home = os.environ.get('EPICS_HOME')

__version__ = 'v0.1.5 2025-04-26'# added 'process' to better track of processes

# abbreviations:
help,cmd,process,cd = ['help','cmd','process','cd']

#``````````````````Properties, used by manman`````````````````````````````````
title = 'Peak Simulator'
startup = {
#       Operational managers
# liteServer-based
'peakSimulator':{help:
  'Lite server, simulating peaks and noise',
  cmd:		'python3 -m liteserver.device.litePeakSimulator -ilocalhost -p9701',
  process:	'litePeakSimulator -ilocalhost -p9701',
  },
'plot it':{help:
  'Plotting tool for peakSimulator',
  cmd:		'python3 -m pvplot -a L:localhost;9701:dev1: x,y',
  process:	'pvplot -a L:localhost;9701:dev1: x,y',
  },
'control it':{help:
  'Automatic parameter editing tool of the peakSimulator',
  cmd:		'python3 -m pypeto -aLITE localhost;9701:dev1',
  process:	'pypeto -aLITE localhost;9701:dev1',
  },
'control&plot':{help:
  'Parameter editing with integrated plot',
  cmd:		'python3 -m pypeto -c config -f peakSimPlot',
  process:	'pypeto -c config -f peakSimPlot',
  #Note: It will look for config file: config/peakSimPlot_pp.py
  },
}
if epics_home is not None:
    startup.update({
# EPICS IOCs
'simScope':{help:
  'EPICS testAsynPortDriver, hosting a simulate oscilloscope',
  cd:f'{epics_home}/asyn/iocBoot/ioctestAsynPortDriver/',
  cmd:'screen -d -m -S simScope ../../bin/linux-x86_64/testAsynPortDriver st.cmd',
  process:'testAsynPortDriver st.cmd', 
},
#'tst_caproto_ioc':  {cmd:'python3 -m caproto.ioc_examples.simple --list-pvs',help:
#  'Simple IOC for testing EPICS Channel Access functionality'},
'pet_simScope':{help:
  'Parameter editing tool for simScope',
  cmd:  'python3 -m pypeto -f Controls/EPICS/simScope',
  },
})

#       Managers for testing and debugging
startup.update({
'tst_sleep30':{help:
  'sleep for 30 seconds', 
  cmd:'sleep 30', process:'sleep 30'
  },
})
