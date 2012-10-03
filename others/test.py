from pxssh import pxssh

hostname = raw_input("Hostname: ")
username = raw_input("Username: ")
password = raw_input("Password: ")

remote = pxssh( )
remote.login( hostname, username, password )
remote.prompt()
