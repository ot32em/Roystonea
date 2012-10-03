__author__ = 'Ot Chen'

start
start -x $xmlfile ! remote startup script
start -t cloud/cluster/rack/node/subsystem -h $ip -p $port

status
''' 10secs ~ 30secs interval to check whether each node alive '''

close

