#! /usr/bin/python

import socket
import threading
from time import sleep
import sys
import inputbox
from bridgeSprites import Button

class bridgeConnection(userInterfaceWindow):
    
    def __init__(self):
		
	self.HOST = raw_input("HOST IP : ")
	self.PORT = 50000
	self.DATA_SIZE = 128 # maximum data length which can be sent in once
	self.myIP = myIPaddress()
	
	self.endThread = False
	self.startGame = False
	self.clients = []
	
	self.makeConnection()
	
	self.sendData("info:connMade:%s;%s"%(self.userName, self.myIP))
	
	self.dataList = {'cmd':[],'grid':[]} #Sort the type of the data
	if not self.soc:
	    print "Server is not opened"	
	
	while not startGame:
	    self.lobby(self.clients)

    def makeConnection(self):
	# make socket and connect to the server
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	soc.settimeout(5.0) # maximum wating time (seconds)
	    
	connected = False
	while not connected:
	    try:
		print "trying to connect " + self.HOST
		soc.connect( (self.HOST, self.PORT) )
		connected = True
		print "Connected!"
		#soc.settimeout(None)
		break
	    
	    except socket.timeout:
		print "Exceeded time limit"
		connectAgain = raw_input("try again?(y/n)")
		if connectAgain == "y" or connectAgain == "Y":
		    continue
		else:
		    return

	    except socket.error:
		print "Access denied"
		sleep(1)
		# [ NOT YET ] if QUIT command is received, call 'sys.exit'
		self.soc = False
		return
	
	self.soc = soc
	# Threading allows to get data whenever it's delievered
	self.T = threading.Thread(target = self.receiveData)
	self.T.start()	

    def sendData(self, data):
	""" Send data (string type) to the server """
	if len(data) <= self.DATA_SIZE:
	    self.soc.send(data.encode('UTF-8'))
	    #print "Data '%s' is sent successfully" %data
	else:
	    print "Data packet size exceeded!"
	
    def receiveData(self):
	""" Receive data (string type) from the server """
	while not self.endThread:
	    try:
		data = self.soc.recv(self.DATA_SIZE) # receive data whose length <= DATA_SIZE
		print "data is : %s" %data
	    except socket.timeout:
		#print "socket timed out"
		continue
	    except:
		print "Connection is lost"
		break
	    
	    if "info:connList" in data:
		self.clients = list(data.split(":")[-1])
	    elif data=='initialize': 
		self.dataList['cmd'].append( data ) # save the received data
            else:
                self.dataList['grid'].append( data)
	self.soc.close() # disconnect the connection
    
    def disconnect(self):
	
	self.endThread = True
	print "joining the thread..."
	self.T.join()
	print "thread is joined"
	pygame.quit()
	sys.exit()
	
class userInterfaceWindow():
    
    def __init__(self, screen):
	
	self.screen = screen
	self.clients = []
	self.userName = inputbox.ask(screen, "Type your name ")
	
	self.buttonColor = (200,20,20)
	self.buttonSize = (50,50,200,50)
	self.buttonPos = (50,50)
	self.myButton = Button(self.buttonPos, self.buttonSize,
				self.buttonColor, self.userName)
	
    def lobby(self, clients):
	
	self.buttonList = [ self.myButton ]
	
	i = 1
	for client in clients:
	    newButtonPos = (self.buttonPos[0], self.buttonPos[1] + 50*i)
	    newUserName = client.split(";")[0]
	    if self.userName == newUserName:
		continue
	    self.buttonList.append( Button(newButtonPos, self.buttonSize, 
				    self.buttonColor, newUserName) )
	    i += 1
	
	for button in buttonList:
	    button.draw(self.screen)


	
def myIPaddress():
    
    try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("gmail.com",80))
	myip = s.getsockname()[0]
	s.close()
	return myip
    except:
	print "Internet disconnected?"
	return 0

if __name__ == "__main__":
    client = bridgeConnection()
    sleep(15)    
    print "end session"
    client.disconnect()
    
