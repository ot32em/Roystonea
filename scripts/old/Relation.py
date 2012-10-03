'''
class:
Unit( BaseUnit, CloudUnit, ClusterUnit, RackUnit, NodeUnit)
	__init__(name, address, parent=None)
	var:
		name: string
		ip: string
		port: int
		children: dictionary(unitname->Unit)
		parent: Unit
	method:
		createChild(name:string, address:turple(ip:string, port:int) )
			return Unit

class:

UnitCollection
	var:
		unitsDict: dictionary('cloud'->dictionary(unitname->Unit),
							  'cluster'->dictionary(unitname->Unit),
							  'rack'->dictionary(unitname->Unit),
							  'node'->dictionary(unitname->Unit)
							  )
	class scope method:
		getFirstCloud()
		getCloudByName(name:string)
		getCloudByAddress(address)
		getClusterByName(name:string)
		getClusterByAddress(address)
		getRackByName(name:string)
		getRackByAddress(address)
		getNodeByName(name:string)
		getNodeByAddress(address)
			above all return Unit
			above address=turple(ip:string, port:int)

		loadXml(XMLPath:string) default xml path: Relation_cfg.xml
			no return	
'''

from xml.dom import minidom,Node
class UnitTypeError(Exception) : pass
class NameExistsError(Exception) : pass

'''
	Unit Classes: base, cloud, cluster, rack, node
'''
class BaseUnit(object) :
	__mytype__='base'
	unitsType = ('cloud', 'cluster', 'rack', 'node')
	def __init__ (self, name, address, parent=None):
		self.name = name
		self.ip, self.port = address
		self.parent = parent
		self.children = dict()
	
	def dump(self, level=0) :
		"dump its name and address(ip:port) and iteratively traverse its children"
		print("\t"*level + "%s@%s:%s" % (self.name, self.ip, self.port ) )
		for name in self.children :
			self.children[name].dump(level+1)

class CloudUnit (BaseUnit) :
	__mytype__='cloud'
	def createChild(self, name, address) :
		child = ClusterUnit(name, address, parent=self)
		self.children[name] = child
		return child

class ClusterUnit (BaseUnit) :
	__mytype__='cluster'
	def createChild(self, name, address) :
		child = RackUnit(name, address, parent=self)
		self.children[name] = child
		return child
	
class RackUnit (BaseUnit) :
	__mytype__='rack'
	def createChild(self, name, address) :
		child = NodeUnit(name, address, parent=self)
		self.children[name] = child
		return child

class NodeUnit (BaseUnit) :
	__mytype__='node'

'''
	Collection Class created for searching unit by its global dic 'unitsDict' variable
'''
class UnitCollection (object) :
	
	'''
	initial Dict
	'''
	unitsType=BaseUnit.unitsType
	unitsDict=dict().fromkeys(unitsType, dict())
	@classmethod
	def resetUnitsDict(cls) :
		cls.unitsDict.fromkeys(cls.unitsType, dict() )

	'''
	Following 2 methods are used to create unit instance
	Main purpose is "REGISTER UNIT' in unitsDict!
	'''
	@classmethod
	def createUnit(cls, name, address, unitType) :
		''' Register the unit to be created '''

		# Validate Parameter
		if not unitType in cls.unitsType : 
			raise UnitTypeError('Unvalid UnitType(%s)' % unitType)
		if name in cls.unitsDict[unitType] : 
			raise NameExistsError("Exists a name(%s)" % name )
		
		# Intance Creation
		if unitType == 'node' :
			unit = NodeUnit( name, address)
		elif unitType == 'rack' :
			unit = RackUnit( name, address)
		elif unitType == 'cluster': 
			unit = ClusterUnit( name, address)
		elif unitType == 'cloud': 
			unit = CloudUnit( name, address)

		# Register to global dict
		cls.unitsDict[unitType][name] = unit
		return unit

	@classmethod
	def createUnitBy(cls, name, address, by ):
		''' Let 'by' unit create child, then `register` the child '''
		child = by.createChild(name, address)
		cls.unitsDict[child.__mytype__] = child 
		return child

	'''
	Following 2+8 methods(2 for base, 8 for node,rack,cluster,cloud) provided for
	search unit by two supporting ways 1.Address=(ip, port) and 2.Name(unit name)
	'''
	# get unit not public
	@classmethod
	def __getUnitByName(cls, unitType, name) :
		return cls.unitsDict[unitType].get(name)
	@classmethod
	def __getUnitByAddress(cls, unitType, address) :
		for unit in cls.unitsDic[unitType].values() :
			if unit.address == address :
				return dic[name]
		return None
	
	# get cloud unit
	@classmethod
	def getCloudByName(cls, name) :	
		return cls.__getUnitByName('cloud', name)
	@classmethod
	def getCloudByAddress(cls, address) : 
		return cls.__getUnitByAddress('cloud', address)
	@classmethod
	def getFirstCloud(cls):
		return cls.unitsDict['cloud'].values()[0] if len(cls.unitsDict['cloud']) > 0 else None

	# get cluster unit
	@classmethod
	def getRackByName(cls, name) :	
		return cls.__getUnitByName('rack', name)
	@classmethod
	def getRackByAddress(cls, address) : 
		return cls.__getUnitByAddress('rack', address)

	# get rack unit
	@classmethod
	def getRackByName(cls, name) :	
		return cls.__getUnitByName('rack', name)
	@classmethod
	def getRackByAddress(cls, address) : 
		return cls.__getUnitByAddress('rack', address)

	# get node unit
	@classmethod
	def getNodeByName(cls, name) :	
		return cls.__getUnitByName('node', name)
	@classmethod
	def getNodeByAddress(cls, address) : return cls.__getUnitByAddress('node', address)
	
	'''
	Load the predefined relationship written in XML file
	'''
	@classmethod
	def loadXml(cls, path='Relation_cfg.xml') :
		"Load the XML format config file to create Relationship"

		cls.resetUnitsDict()
		doc = minidom.parse(path)
		for cloudElement in doc.getElementsByTagName('Cloud') :
			cloudName = cloudElement.getAttribute('name')
			cloudIp = cloudElement.getAttribute('ip')
			cloudPort = int( cloudElement.getAttribute('port') )
			cloudUnit = cls.createUnit(cloudName, (cloudIp, cloudPort), 'cloud')
			for clusterElement in cloudElement.childNodes :
				if clusterElement.nodeType != Node.ELEMENT_NODE : continue # skip text_node
				clusterName = clusterElement.getAttribute('name')
				clusterIp = clusterElement.getAttribute('ip'),
				clusterPort = int( clusterElement.getAttribute('port')  )
				clusterUnit = cls.createUnitBy(clusterName, ( clusterIp, clusterPort), by=cloudUnit )
				for rackElement in clusterElement.childNodes :
					if rackElement.nodeType != Node.ELEMENT_NODE : continue # skip text_node
					rackName = rackElement.getAttribute('name')
					rackIp = rackElement.getAttribute('ip'),
					rackPort = int( rackElement.getAttribute('port') )
					rackUnit = cls.createUnitBy(rackName, (rackIp, rackPort), clusterUnit )
					for nodeElement in rackElement.childNodes :
						if nodeElement.nodeType != Node.ELEMENT_NODE : continue #skip text_node
						nodeName = nodeElement.getAttribute('name')
						nodeIp = nodeElement.getAttribute('ip')
						nodePort = int( nodeElement.getAttribute('port') )
						nodeUnit = cls.createUnitBy(nodeName,( nodeIp, nodePort), by=rackUnit )

# end of class Unit						

if __name__ == '__main__' :
	UnitCollection.loadXml()
	top = UnitCollection.getFirstCloud() # get the only one cloud unit at top
	top.dump()
