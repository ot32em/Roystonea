from fabric.api import *
from cuisine import *
import os

env.hosts = ['140.112.28.240']
env.user = "rayshih"
env.forward_agent = True

git_repository = 'git@github.com:ot32em/Roystonea.git'
deploy_to = '/home/%(user)s/deploy' % ({'user': env.user})

def host_type():
	run("uname -s")

def clone_from_github():
	dir_ensure(deploy_to)
	with cd(deploy_to):
		git_dir = os.path.join(deploy_to, 'Roystonea')
		if dir_exists(git_dir):
			with cd(git_dir):
				run('git checkout -- .')
				run('git pull')
		else:
			run('git clone %s' % git_repository)


