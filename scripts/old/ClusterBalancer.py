#import roystonea_package.Message
from scripts.include import Message

def ClusterBalancer(req):
	return Message.ClusterHyperVisorRt(status='Cool', msg=str(req.name)*3)
