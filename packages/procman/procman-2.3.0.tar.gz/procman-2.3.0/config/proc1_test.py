'''Definition of the second test apparatus.
'''
import os
homeDir = os.environ['HOME']

__version__ = 'v0.0.2 2025-09-14'# shell:True in htop

# abbreviations:
help,cmd,process,cd,shell = ['help','cmd','process','cd','shell']

#``````````````````Properties, used by manman`````````````````````````````````
title = 'Test applications'

startup = {
'xclock':{help:'Digital xclock', 
  cmd:'xclock -digital'
  },
'htop':{help:'Process viewer in separate xterm',
  cmd:'xterm -e "htop; bash"',
  shell:True,
  process: 'xterm -e htop',
  },
'sleep30':{help:'Sleep for 30 seconds', 
  cmd:'sleep 30', process:'sleep 30'
  },
}
