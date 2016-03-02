#! /usr/bin/python

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import socket, sys
from time import sleep
import pygame

myhost = '127.0.0.1'

class Server(Protocol):
    
    def __init__(self):
	
	self.connList = []
	
    def connectionMade(self):
	
        self.factory.clients.append(self)
        
        self.peer = self.transport.getPeer()
        print vars(self.peer) # show who made the connection

        if self.peer.host == myhost:
            self.factory.host = self
        
        """ Initialize the game when enough players are connected """
        #if len(self.factory.clients) == 2:
	    #print "2 players are joined!"
	    #sleep(2.5) # wait before starting the game
            #self.message_all('initialize') # when clients receive this msg, they starts the game
            
    def connectionLost(self, reason):
	""" When a client lose a connection """
        print "connection lost ", self
        
        # Erase lost client from self.connList
        # and send the updated self.connList
        for conn in self.connList[:]:
	    if conn.split(";")[1] == self.transport.getPeer().host:
		self.connList.remove(conn)
		self.message_all("info:connList:%s" %str(self.connList))
		break
	
	# Erase lost client from self.factory.clients
	self.factory.clients.remove(self)

    def dataReceived(self, data):
	""" If data is delivered from a client to the server,
	    deliver the data to other clients """
        sender = self.transport.getPeer().host # address of data sender
	print "received data is : " + data
        self.message_all(data)
        
        # save client to self.connList
        # and send the updated self.connList
        if "info:connMade:" in data:
	    splited = data.split(":")[-1].split(";") # [ userName, IP ]
	    for client in self.factory.clients:
		newConn = "%s;%s" %(splited[0],splited[1])
		if newConn not in self.connList[:]:
		    self.connList.append(newConn)
		    self.message_all("info:connList:%s" %str(self.connList))
		    break
	print self.connList
	
    def message_all(self, msg):
	""" Send message to all clients from server """
        for clients in self.factory.clients:
            clients.transport.write(msg+"^")

    def message_to(self, clients_num, msg):
	""" Send message to a certain client from server """
        if clients_num in range(1, len(self.factory.clients) + 1):
            self.factory.clients[clients_num].transport.write(msg + '\n')
            
    #def connectionList(self):
	
	#self.connList = []
	#for client in self.factory.clients:
	    #self.connList.append(client.transport.getPeer().host)
	    
	#self.message_all("info:connList:%s"%str(self.connList))
	
def hostIPaddress():      
    try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("gmail.com",80))
	myhostip = s.getsockname()[0]
	s.close()
	return myhostip
    except:
	print "Internet disconnected?"
	return 0

if __name__ == "__main__":
    myhostip = hostIPaddress()
    if not myhostip:
	sys.exit()
    factory = Factory()
    factory.protocol = Server
    factory.clients = [] # clients list
    factory.host = None

    PORT = 50000 # port of the server
    reactor.listenTCP(PORT, factory)
    print "[ Server info ]\nServer IP : %s\nPort : %d" %(myhostip, PORT)
    print "Server is now running.\nPress [ Ctrl-c ] to close the server."
    reactor.run()