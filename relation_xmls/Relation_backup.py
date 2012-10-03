from xml.dom import minidom,Node

class Unit (object) :

	# all the units registered in class variable "unitsDict"
	# then it used by following getUnitByName(), getUnitByAddress() class scope methods
	# to search any Units You want
	unitsType=('cloud', 'cluster', 'rack', 'node' )
	unitsDict= dict()
	unitsDict.fromkeys(unitsType, dict())

	unitsType=unitsDict.keys()
	def __init__ (self, name, address, parent):
		self.name = name
		self.ip, self.port = address
		self.parent = parent
		self.children = dict()

	@classmethod
	def resetUnitsDict(cls) :
		del cls.unitsDict
		cls.unitsDict = {'cloud': dict(), 'cluster':dict(), 'rack':dict(), 'node':dict() }

	@classmethod
	def createUnit(cls, name, address, unitType) :
		'''
		check unitType, check repeat name
		create a instance and register into unitsDict
		'''
		# validate unitType
		if not unitType in cls.unitsDict : 
			raise Exception("unitType: %s is unvalid" % unitType)
		# cannot create repeat name
		if name in cls.unitsDict[unitType] : 
			raise Exception("name: %s repeat" % name )

		# create each instance of defferent type
		if unitType == 'node' :
			unit = NodeUnit( name=name, address=address, parent=None )
		elif unitType == 'rack' :
			unit = RackUnit( name=name, address=address, parent=None )
		elif unitType == 'cluster': 
			unit = ClusterUnit( name=name, address=address, parent=None )
		elif unitType == 'cloud': 
			unit = CloudUnit( name=name, address=address )
		# register to global dict
		cls.unitsDict[unitType][name] = unit
		return unit
		

	def createChild(self, name, address, childType ):
		'''
		perform createUnit() method
		then set child instance's parent = self
		'''
		child = Unit.createUnit( name=name, address=address, unitType=childType)
		child.parent = self
		self.children[name] = child 
		return child

	@classmethod
	def getUnitByName(cls, unitType, name) :
		''' 
		search unit by name
		'''
		if not unitType in cls.unitsDict :
			raise Exception("Wrong unitType:%s" % unitType )
		return cls.unitsDict[unitType].get( name, None)

	@classmethod
	def getUnitByAddress(cls, unitType, address) :
		'''
		search unit by address, address type is a turple (ip, port)
		i think byAddress might be more useful than byName in the future~
		'''
		if not unitType in cls.unitsDict : 
			raise Exception("Wrong unitType: %s" % unitType )
		dic = cls.unitsDict[unitType]
		for name in dic :
			if dic[name].address == address :
				return dic[name]
		return None

	@classmethod
	def getTop(cls) :
		''' 
		Make sure two conditions to use getTop method
		1.There is a cloud unit exists
		2.Only one cloud unit exists
		because it just return unitsDict['cloud'][0] and make for quick access in small scale
		'''
		for name in cls.unitsDict['cloud'] :
			return cls.unitsDict['cloud'][name]

	@classmethod
	def loadCfg(cls, path='Relation_cfg.xml') :
		"Load the XML format config file to create Relationship"

		cls.resetUnitsDict()
		doc = minidom.parse(path)
		for cloudElement in doc.getElementsByTagName('Cloud') :
			cloudName = cloudElement.getAttribute('name')
			cloudIp = cloudElement.getAttribute('ip')
			cloudPort = int( cloudElement.getAttribute('port') )

			try: 
				cloudUnit = Unit.createUnit(name=cloudName,	address=(cloudIp, cloudPort), unitType='cloud' )
			except Exception as msg :
				cls.resetUnitsDict()
				raise Exception("cannot create(%s) cloudUnit(%s@%s:%d) in loadCfg" % (msg, cloudName, cloudIp, cloudPort) )
				
			for clusterElement in cloudElement.childNodes :
				if clusterElement.nodeType != Node.ELEMENT_NODE : continue # skip text_node
				clusterName = clusterElement.getAttribute('name')
				clusterIp = clusterElement.getAttribute('ip'),
				clusterPort = int( clusterElement.getAttribute('port')  )

				try:
					clusterUnit = cloudUnit.createChildCluster(	name=clusterName, address=( clusterIp, clusterPort) )
				except Exception as msg :
					cls.resetUnitsDict()
					raise Exception("cannot create(%s) clusterUnit(%s@%s:%d) in loadCfg" % (msg, clusterName, clusterIp, clusterPort) )

				for rackElement in clusterElement.childNodes :
					if rackElement.nodeType != Node.ELEMENT_NODE : continue # skip text_node
					rackName = rackElement.getAttribute('name')
					rackIp = rackElement.getAttribute('ip'),
					rackPort = int( rackElement.getAttribute('port') )

					try:
						rackUnit = clusterUnit.createChildRack(	name=rackName, address=(rackIp, rackPort) )
					except Exception as msg :
						cls.resetUnitsDict()
						raise Exception("cannot create(%s) rackUnit(%s@%s:%d) in loadCfg" % (msg, rackName, rackIp, rackPort) )

					for nodeElement in rackElement.childNodes :
						if nodeElement.nodeType != Node.ELEMENT_NODE : continue #skip text_node
						nodeName = nodeElement.getAttribute('name')
						nodeIp = nodeElement.getAttribute('ip')
						nodePort = int( nodeElement.getAttribute('port') )

						try: 
							nodeUnit = rackUnit.createChildNode( name = nodeName, address = ( nodeIp, nodePort) )
						except Exception as msg :
							cls.resetUnitsDict()
							raise Exception("cannot create(%s) nodeUnit(%s@%s:%d) in loadCfg" % (msg, nodeName, nodeIp, nodePort) )

	def dump(self, level=0) :
		'''
		dump its name and address(ip:port) and iteratively traverse its children
		'''
		print("\t"*level),
		print("%s@%s:%s" % (self.name, self.ip, self.port ) )
		for name in self.children :
			self.children[name].dump(level+1)
# end of class Unit						



class CloudUnit (Unit) :
	'''
	remember! Cloud __init__ parameters has no parent!
	'''
	def __init__ (self, name, address) :
		# Cloud is top level with no parent
		Unit.__init__(self, name=name, address=address, parent=None)
	def createChildCluster(self, name, address) :
		return self.createChild(name=name, address=address, childType='cluster')

class ClusterUnit (Unit) :
	def createChildRack(self, name, address) :
		return self.createChild(name=name, address=address, childType='rack')
	
class RackUnit (Unit) :
	def createChildNode(self, name, address) :
		return self.createChild(name=name, address=address, childType='node')

class NodeUnit (Unit) :
	pass

if __name__ == '__main__' :
	Unit.loadCfg()
	top = Unit.getTop() # get the only one cloud unit at top
	top.dump()
