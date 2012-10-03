'''
This package contains the modules used to create a machine

by Elalic, 2011.07.15
'''

__all__ = ['Node', 'Rack', 'Cluster', 'Cloud']

import pexpect
import socket


class machine(object):

	def __init__(self, cfgpath):
		'''
		Default settings.
		'''
		
		(hostname, retv) = pexpect.run('hostname')
		if retv != 0 :
			#XXX raise exceptions 
		ip = socket.gethostbyname(hostname)
		if myname:
			name = hostname
		else:
			name = ip

		log.path = '/tmp/roystonea-%s.log'%()

		'''
		Load settings from controller.
		'''

		'''
		Load settings from config file.
		'''
		if os.access(cfgpath, os.R_OK):
			execfile(cfgpath)
		else:
			#XXX raise exceptions 
		storage.path = '/var/SFS/'

		hyperviosor.cmd.create = 'xm create'
		hyperviosor.cmd.shutdown = 'xm shutdown'
		hyperviosor.cmd.destroy = 'xm destroy'
