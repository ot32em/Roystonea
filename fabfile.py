from fabric.api import *
from cuisine import *
import os

env.hosts = ['140.112.28.240']
env.user = "royuser"
env.forward_agent = True

GIT_REPOSITORY = 'git@github.com:ot32em/Roystonea.git'
APP_NAME = 'Roystonea'
DEPLOY_TO = '/home/%(user)s/deploy' % ({'user': env.user})
APP_ROOT = os.path.join(DEPLOY_TO, APP_NAME)

def install():
	run("curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python")
	run("sudo pip install pystache")

def deploy():
	clone_from_github()

def host_type():
	run("uname -s")

def clone_from_github():
	dir_ensure(DEPLOY_TO)
	with cd(DEPLOY_TO):
		if dir_exists(APP_ROOT):
			with cd(APP_ROOT):
				run('git checkout -- .')
				run('git pull')
		else:
			run('git clone %s' % GIT_REPOSITORY)

# VM Test
# ubuntu
def test_vm(vm_type, action=None):
    if action:
        _test_vm(vm_type,action)
    else:
        _test_vm(vm_type, "start")
        _test_vm(vm_type, "listVM")
        _test_vm(vm_type, "shutdown")

def test_portmapping(action):
    if action == 'a':
        test_vm('ubuntu', 'start')
        _test_portmapping(action)
    else:
        _test_portmapping(action)
        test_vm('ubuntu', 'shutdown')

def tmp_test_portmapping(action):
    with cd(APP_ROOT):
        run("sudo python royctl.py run portmapping_test 'try_pm(\"%(action)s\")'" % ({'action': action}))

def _test_vm(vm_type, command):
    with cd(APP_ROOT):
        run("sudo python royctl.py run vm_manager.vm_%(vm_type)s_manager 'test(\"%(command)s\")'" % ({'vm_type': vm_type, 'command': command}))

def start_algorithm_server():
    with cd(APP_ROOT):
        run("sudo python royctl.py run algorithm 'start(5000)'")

