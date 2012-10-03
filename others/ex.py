class people (object) :
	ps = dict

class person (object) :
	def __init__ (self, name ) :
		self.name = name
		

a = person("John")
b = person("killme")
print( a.name )
print( b.name )
