from fabric.api import *
from cuisine import *
import os

env.hosts = ['140.112.28.240']
env.user = "rayshih"
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
def test_vm(vm_type):
    _test_vm(vm_type, "start")
    _test_vm(vm_type, "listVM")
    _test_vm(vm_type, "shutdown")

def _test_vm(vm_type, command):
	with cd(APP_ROOT):
        run("sudo python royctl.py run vm_manager.vm_%(vm_type)s_manager 'test(\"%(command)s\")'" % ({'vm_type': vm_type, 'command': command}))
