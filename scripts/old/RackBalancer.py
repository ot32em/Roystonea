#import roystonea_package.Message
from scripts.include import Message

def RackBalancer(req):
	return Message.RackHypervisorRt(status='good', msg='i am RB '+str(req.name)*3)
