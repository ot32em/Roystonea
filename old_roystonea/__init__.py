'''This is Roystonea package __init__.py'''

__all__ = []

'''
CloudController.py
	#It knows that each user accout hold by which ClusterController.

ClusterController.py
	Coordinator.py
		Database Subsystem
			Request Database
			Monitor Database
			User Accout
		VM Prototype
	VMManager
		Rack Placement

RackController.py
	VMManager
		Node Placement
		Node Consolidator
			#Across node consolidation
	Subsystem Manager
		Hypervisor Manager
		Networking Manager
		Monitoring Manager
		Storage Manager

NodeController.py
	Subsystem Manager
		Hypervisor Manager
		Networking Manager
		Monitoring Manager
		Storage Manager
'''

