import _mysql
import time
import threading
from scripts.include import Message

'''This is default ClusterDatabaseSubsystem'''
class ClusterDatabaseSubsystem():

	def GetAvailablePhysicalMachine(self, req, cfg):
		import _mysql

		x = Message.GetAvailablePhysicalMachineRt(msg='i am GAPM'
							     + ' '
							     + cfg.rest['ClusterBalancerPath']
							     + req.auth)
		return x
		#print 'i am GAPM'+req.auth

class ClusterPrototypeSubsystem():

	def GetAvailableVirtualMachinePrototype(self, req, cfg):
		return Message.GetAvailableVirtualMachinePrototypeRt(msg='i am GAVMP: '+req.auth)

class ClusterLoggingSubsystem():
		pass

class ClusterCoordinator():

	def __init__(self, cfg):
		'''Temporary used'''
		self.cfg_dict = cfg.rest
		self.server = cfg.rest.get('ClusterDBAddr')
		self.username = cfg.rest.get('ClusterDBUsername')
		self.passwd = cfg.rest.get('ClusterDBPassword')
		self.dbname = cfg.rest.get('ClusterDBName')
		self.requesttb = cfg.rest.get('ClusterReqTb')
		self.sleep_time = cfg.rest.get('ClusterDBChkInterval')
		'''
		self.server = 'localhost'
		self.username = 'root'
		self.passwd = '86888'
		self.dbname = 'roystonea_cluster'
		self.requesttb = 'request'
		self.sleep_time = 5'''
		self.connect_db()

	def process_request_thread(self, *args):
		'''Coordinator handler'''
        	try:
			(id, user, vmnum, vmcores, vmmem, vmdisk, vmtype, timest, val, state) = args
			_req = {'id': id,
				'vm_num': vmnum,
				'vm_cores': vmcores,
				'vm_mem': vmmem,
				'vm_disk': vmdisk,
				'vm_type': vmtype,
				'timestamp': timest,
				'validity': val}
			print 'request id: '+_req['id']+' start'
			#update database as pendding
			#call Racks, or the right one to handle the request
			#just like *_client.py
		except:
			#if the request fail, update req state to failure
			pass
	
		print 'request id: '+_req['id']+' end'
		return 

	def process_request(self, request):
		"""Start a new thread to process the request."""
		t = threading.Thread(target = self.process_request_thread, args = (request))
		t.setDaemon(1)
		t.start()

	def connect_db(self):
		try:
			self.db =_mysql.connect(host = self.server, 
					       user = self.username, 
					       passwd = self.passwd, 
					       db = self.dbname)
		except Exception, e:
			self.db = None
			print str(e)

	def run(self):
		while True:
			#check database
			query_request = \
			     "SELECT * FROM %s WHERE state='new' ORDER BY timestamp" \
			     %(self.requesttb)
			try:
				self.db.query(query_request)
				req_res = self.db.store_result()
				fetched_req_data = req_res.fetch_row(0)

			#process request
				for req in fetched_req_data:
					req_tabble = {
						'id': req[self.cfg_dict.get('ClusterReqTb_Id')],
						'user': req[self.cfg_dict.get('ClusterReqTb_User')],
						'vm_num': req[self.cfg_dict.get('ClusterReqTb_VMnumber')],
						'vm_cores': req[self.cfg_dict.get('ClusterReqTb_VMcores')],
						'vm_mem': req[self.cfg_dict.get('ClusterReqTb_VMmem')],
						'vm_disk': req[self.cfg_dict.get('ClusterReqTb_VMdisk')],
						'vm_type': req[self.cfg_dict.get('ClusterReqTb_VMtype')],
						'timestamp': req[self.cfg_dict.get('ClusterReqTb_Timest')],
						'validity': req[self.cfg_dict.get('ClusterReqTb_Validity')],
						'state': req[self.cfg_dict.get('ClusterReqTb_State')],
					}
					self.process_request(req_tabble)
			except Exception, e:
				self.db = None
				print str(e)

			#sleep
			time.sleep(self.sleep_time)

if __name__ == '__main__':
	class cfg():
		_dict = {}
	mycfg = cfg()
	execfile('default_cfg', mycfg.rest)
	coordinator = ClusterCoordinator(mycfg)
	coordinator.run()

