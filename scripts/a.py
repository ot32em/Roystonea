import include.message as msg 
import include.client as client
myaddr = ("localhost", 4001 )
dest_addr = ("localhost", 7001 )
rack_unit = {"host": "localhost", "port":1003 }

req = msg.MonitorAskNodeListReq( [rack_unit], myaddr, 1 )
res = client.send_message( dest_addr, req )
print( res )
