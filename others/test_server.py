# from socket import socket, AF_INET, SOCK_STREAM
# import SocketServer
# from scripts.include.ThreadPoolMixIn import ThreadPoolTCPServer
# import threading
# import time
# 
# class TimeReportHandler(SocketServer.BaseRequestHandler) :
# 	def handle(self) :
# 		threading_name = threading.current_thread().getName()
# 		current_time = time.ctime()
# 		client_address = self.client_address
# 		print("Got request from %s:%s" % (client_address[0], client_address[1]) )
# 		response = "Now is %s, This is %s serving for you." % ( current_time, threading_name)
# 		self.request.send( response )
# 		self.request.close()
# 
# class TimeReportClient():
# 	def __init__(self, ip='localhost', port=12345):
# 		self.ip = ip
# 		self.port = port
# 
# 	def get_report(self):
# 		self.socket = socket(AF_INET, SOCK_STREAM)
# 		self.socket.connect( (self.ip, self.port))
# 		result = self.socket.recv(1024)
# 		print( result )
# 		self.socket.close()
# 
# 	def get_lots_report(self, times):
# 		for i in xrange( times ):
# 			t = threading.Thread(target=self.get_report)
# 			t.start()
# 			t.join()
# 
# if __name__ == '__main__' :
# 	HOST = 'localhost'
# 	PORT = 12345
# 	class TimeReportServer(ThreadPoolTCPServer) :
# 		def __init__(self) :
# 			ThreadPoolTCPServer.__init__(self, server_address=(HOST, PORT),
# 											RequestHandlerClass=TimeReportHandler)
# 	trs = TimeReportServer()
# 	trs.serve_forever()
# 
# 		
# 		
