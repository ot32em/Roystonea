'''
This is user specefied machine list
e.g.
Cloud
	Cluster
		Rack
			Node
			Node
			Node
	Cluster
		Rack
			Node
			Node
		Rack
			Node
----------------------------------	
192.168.10.70
	192.168.10.70
		192.168.10.70
			192.168.10.70
			192.168.10.71
			192.168.10.72
	192.168.10.73
		192.168.10.74
			192.168.10.74
			192.168.10.75
		192.168.10.76
			192.168.10.77
----------------------------------
Cloud = ['192.168.10.70']
Cluster = ['192.168.10.70', '192.168.10.73']
Rack = ['192.168.10.70', '192.168.10.74', '192.168.10.76']
Node = ['192.168.10.70', '192.168.10.71', '192.168.10.72', '192.168.10.73', '192.168.10.74', '192.168.10.75', 
	'192.168.10.76', '192.168.10.77']
---------------------------------------------------
'''
node0 = '192.168.10.70'
node1 = '192.168.10.71'
node2 = '192.168.10.72'
node3 = '192.168.10.73'
node4 = '192.168.10.74'
node5 = '192.168.10.75'
node6 = '192.168.10.76'
node7 = '192.168.10.77'

rack1(node0) = [node0, node1, node2]
rack2(node4) = [node4, node5]
rack3(node6) = [node7]

cluster1(node0) = [rack1]
cluster2(node6) = [rack2, rack3]

cloud(node0) = [cluster1, cluster2]
