from scripts.include import Message

'''This is default CloudCoordinator'''
class CloudCoordinator():

	def GetAvailableClusters(self, req, cfg):
		import _mysql
		list_avc = []
		try:
			db = _mysql.connect(host = cfg.rest.get('CloudDBIp'), 
					    user = cfg.rest.get('CloudDBUsername'),
					    passwd = cfg.rest.get('CloudDBPassword'), 
					    db = cfg.rest.get('CloudDBName'))
			sql_query = "SELECT * FROM %s WHERE state='available' ORDER BY id"\
								%(cfg.rest.get('CloudDBClustersTb'))
			db.query(sql_query)
			req_res = db.store_result()
			list_avc = [ x[1] for x in req_res.fetch_row(0)]
		except Exception, e:
			print str(e)


		x = Message.GetAvailableClustersRt(msg='i am GAC'
							     + ' '
							     + cfg.rest['CloudComponentsPath']
							     + req.auth,
						  status='good',
						  avClusters=list_avc)
		return x


