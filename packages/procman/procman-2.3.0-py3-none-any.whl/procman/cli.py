'''Command line tool to start servers and managers
'''
__version__ = 'v0.1.4 2024-10-27'#
import sys, os, time, subprocess, argparse, threading
from functools import partial
from importlib import import_module

from . import helpers as H

Apparatus = H.list_of_apparatus()

ManCmds = ['Check','Start','Stop','Command']

def manAction(manName, cmd):
    H.printv(f'manAction: {manName, cmd}')
    cmdstart = Startup[manName]['cmd']    
    if cmd == 'Check':
        H.printv(f'checking process {cmdstart} ')
        if H.is_process_running(cmdstart):
            print(f'Manager "{manName}" \tstarted')#, process name: "{cmdstart}"')
            return os.EX_OK
        else:
            print(f'Manager "{manName}" \tis not running')
            return os.EX_UNAVAILABLE
            
    elif cmd == 'Start':
        H.printv(f'starting {manName}')
        if H.is_process_running(cmdstart):
            H.printe(f'Manager "{manName}" is already running.')
            return os.EX_CANTCREAT

        cmdlist = cmdstart.split()
        H.printv(f'popen: {cmdlist}')
        try:
            process = subprocess.Popen(cmdlist, #close_fds=True,# env=my_env,
              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception as e:
            H.printe(f'Exception starting {manName}: {e}') 
            return os.EX_IOERR

        time.sleep(5)# 3 is small for PLC device
        H.printv('slept 5 seconds')
        ex = manAction(manName, 'Check')
        if ex != os.EX_OK:
            return os.EX_UNAVAILABLE

    elif cmd == 'Stop':
        H.printv(f'stopping {manName}')
        process = Startup[manName].get('process', f'{cmdstart}')
        cmd = f'pkill -f "{process}"'
        H.printv(f'executing: {cmd}')
        os.system(cmd)
        time.sleep(0.1)
        ex = manAction(manName, 'Check')
        if ex != os.EX_UNAVAILABLE:
            return os.EX_SOFTWARE

    elif cmd == 'Command':
        try:
            cd = Startup[manName]['cd']
            cmd = f'cd {cd}; {cmdstart}'
        except Exception as e:
            cmd = cmdstart
        print(f'Start command for "{manName}": "{cmd}"')
        return os.EX_OK

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      epilog=f'Version {__version__}')
    parser.add_argument('-a','--apparatus', choices=Apparatus, default='TST', help='Which apparatus to control')
    parser.add_argument('-c', '--configDir', default=H.ConfigDir, help=\
      'Directory, containing apparatus configuration scripts')
    parser.add_argument('-m', '--manager', default='all',
help='Apply command to a particular manager (or all) of the apparatus')
    parser.add_argument('-t', '--test', action='store_true',
help='Include non-operational (test) managers') 
    parser.add_argument('-v', '--verbose', action='count', default=0, help=\
      'Show more log messages (-vv: show even more).')
    parser.add_argument('command', nargs='?', choices=ManCmds, default='Check')
    pargs = parser.parse_args()
    H.printv(f'pargs: {pargs}')

    # import the manager
    mname = 'manman.apparatus_'+pargs.apparatus
    module = import_module(mname)
    print(f'imported {mname} {module.__version__}')
    Startup = module.startup
    mname = 'manman.apparatus_'+pargs.apparatus
    module = import_module(mname)

    if pargs.manager == 'all':
        pargs.manager = list(Startup.keys())
    else:
        pargs.manager = [pargs.manager]
    H.printv(f'Managers: {pargs.manager}')

    for manName in pargs.manager:
        if manName not in Startup:
            H.printe(f'Wrong manager, supported are: {",".join(Startup.keys())}')
            sys.exit(os.EX_USAGE)
        if not pargs.test:
            if manName.startswith('tst_'):
                continue
        manAction(manName, pargs.command)

