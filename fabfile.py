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
def vm_ubuntu(command):
	with cd(APP_ROOT):
		run("sudo python scripts/vmstartup/VM_initializer_ubuntu.py %(command)s" % ({'command': command}))
