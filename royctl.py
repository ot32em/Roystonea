import sys
import imp

'''
    some tool
'''
def handleArguments(arg):
    if len(arg) <= 1 or arg[1] in helpCommands():
        help()
    elif arg[1] in startCommands():
        start()
    elif arg[1] in stopCommands():
        stop()
    elif arg[1] in runCommads():
        script_name = arg[2]
        message = arg[3]
        run(script_name, message)
    elif arg[1] in terminalCommands():
        terminal()

def end():
    raise SystemExit

'''
    user input commands match
'''
def helpCommands():     return ('help', '-h', '--help')
def startCommands():     return ('start')
def stopCommands():     return ('stop')
def statusCommands():     return ('status')
def runCommads():       return ('_run')
def terminalCommands(): return ('_terminal')




'''
    real actions
'''
def help():
    print(
'''usage:
    royctl.py help, -h , --help
        Display Supported Commands

    royctl.py start [--xml=(RelationHierachy.xml)] [--config=(etc/startup.cfg)]
        Remotely start every daemon in system configured in xml file .

    royctl.py stop
        Remotely stop all daemons by sending terminal signal to each daemon.

    royctl.py restart
        Stop completed then start with the same setting.

    ---
    royctl.py _run -t [Cluster | Rack | Node | Algorithm | SubsystemManager | Coordinator ] -h (hostname) -p (port)
        Run single daemon with given unique network location.

    royctl.py _terminal [-h (hostname) -p (port) | -label (label) ]
        Terminal single daemon with given unique id.

    ---
    royctl.py status
        Report current status.
'''
    )

def start():
    print('starting')

def stop():
    print('stop')

def run(script_name, message):
    package_name = "scripts.%s" % (script_name)
    scripts = __import__(package_name)
    target = eval(package_name)

    print("run %(script_name)s.%(message)s()" % ({'script_name': script_name, 'message': message}))
    getattr(target, message)()
        


def status():
    print('terminal')

def terminal():
    print('terminal')



if __name__ == '__main__':
    handleArguments( sys.argv )
