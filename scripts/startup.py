import time
addrs = { ('localhost', 7007) : 'rack', 
          ('localhost', 7008) : 'rack', 
          ('localhost', 7009) : 'rack',
          ('localhost', 7010) : 'rack',
          ('localhost', 8003) : 'cluster'}


import pxssh
import threading

def launch( level, addr):
    name = "{host}-{port}".format( host=addr[0], port=addr[1] )
    print("%s launch thread start!" % name )
    remote = pxssh.pxssh()
    isLogin = remote.login('localhost', 'ot32em', '' )
    print("{name} isLogin: {isLogin}".format( name = name, isLogin = isLogin ) )
    script = '/mnt/images/nfs/new_roystonea_script/roystonea_script/'+level+'.py'
    cmd = 'nohup python {script} {host} {port} console_off > {name}.txt'.format( script=script, host=addr[0], port=addr[1], name = name )
    remote.sendline( cmd )
    remote.prompt()
    print("Name {name} pxssh.before: ".format(name = name) )
    print(remote.before )
    remote.logout()

for addr in addrs :
    level = addrs[addr]
    t = threading.Thread( target = launch, kwargs = { 'level': level, 'addr':addr } )
    t.run()


    
