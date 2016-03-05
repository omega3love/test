#! /usr/bin/python

import socket
import threading
from time import sleep
import sys, os
import inputbox
import pygame
from bridgeSprites import Button

class userInterfaceWindow():
    
    def __init__(self, screen):
	
	self.screen = screen
	self.clients = []
	self.userName = inputbox.ask(screen, "Type your name ")
	
	self.buttonColor = (200,20,20)
	self.buttonSize = (200,50)
	self.buttonPos = (50,50)
	self.myButton = Button(self.buttonPos, self.buttonSize,
				self.buttonColor, self.userName)
	
	self.brokenError = False
	
    def lobby(self, clients):
	
	self.screen.fill(-1)
	self.buttonList = [ self.myButton ]
	
	i = 1
	for client in clients:
	    newButtonPos = (self.buttonPos[0], self.buttonPos[1] + 70*i)
	    newUserName = client.split(";")[0]
	    if self.userName == newUserName:
		continue
	    self.buttonList.append( Button(newButtonPos, self.buttonSize, 
				    self.buttonColor, newUserName) )
	    i += 1
	
	for button in self.buttonList:
	    button.draw(self.screen)
	
	for event in pygame.event.get():
	    if event.type == pygame.QUIT:
		self.brokenError = True

	pygame.display.update()
	#pygame.time.Clock().tick(30)
	    
    def askToPlay(self):
	
	mouseDownPos, mouseUpPos = None, None
	buttonDowned = None
	self.waitingForAns = False
	self.switch = True
	
	while True:
	    pygame.event.clear()
	    ev = pygame.event.wait()
	    #print pygame.event.event_name(ev.type)
	    mouseDownPos = None
	    mouseUpPos = None
	    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE or ev.type == pygame.QUIT:
		break
	    elif ev.type == pygame.MOUSEBUTTONDOWN:
		mouseDownPos = pygame.mouse.get_pos()
	    elif ev.type == pygame.MOUSEBUTTONUP:
		mouseUpPos = pygame.mouse.get_pos()
		
	    if not self.waitingForAns:
		isMousePressed = pygame.mouse.get_pressed()[0]
		for button in self.buttonList:
		    xBdry = (button.pos[0], button.pos[0] + button.rect[2])
		    yBdry = (button.pos[1], button.pos[1] + button.rect[3])
		    if mouseDownPos:
			isInBdry = (xBdry[0] <= mouseDownPos[0] < xBdry[1]) and (yBdry[0] <= mouseDownPos[1] < yBdry[1])

			if isMousePressed:
			    if not buttonDowned and isInBdry:
				buttonDowned = button
			    elif buttonDowned == button and not isInBdry:
				buttonDowned = None
			else:
			    buttonDowned = None
		    if mouseUpPos:
			isInBdry = (xBdry[0] <= mouseUpPos[0] < xBdry[1]) and (yBdry[0] <= mouseUpPos[1] < yBdry[1])
			
			if buttonDowned == button and isInBdry:
			    print "Clicked button : " + button.text
			    display_pos = ( button.pos[0]+button.rect[2]+20, button.pos[1] )
			    inputbox.display_msg_custum(self.screen, display_pos, "Asked '%s' to play. Hang on a sec..." %button.text)
			    buttonDowned = None
			    self.waitingForAns = button.text
	    #else:
		
		
		
class bridgeConnection(userInterfaceWindow):
    
    def __init__(self, screen):
			
	#self.HOST = raw_input("HOST IP : ")
	self.HOST = "143.248.12.11"
	self.PORT = 50000
	self.DATA_SIZE = 256 # maximum data length which can be sent in once
	self.myIP = myIPaddress()
	
	self.endThread = False
	self.startGame = False
	
	userInterfaceWindow.__init__(self, screen)
	self.makeConnection()
	self.sendData("info:connMade:%s;%s"%(self.userName, self.myIP))
	
	self.dataHistory = [] # all data must be saved here at first
	self.dataGrave = [] # processed data will be saved here
	self.dataList = {'cmd':[],'grid':[]} #Sort the type of the data
	
	if not self.soc:
	    print "Server is not opened"	

	print "waiting an event..."
	
	self.lobby(self.clients)
	self.askToPlay()

    def makeConnection(self):
	# make socket and connect to the server
	self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	self.soc.settimeout(5.0) # maximum wating time (seconds)
	    
	connected = False
	while not connected:
	    try:
		print "trying to connect " + self.HOST
		self.soc.connect( (self.HOST, self.PORT) )
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
	
	# Threading allows to get data whenever it's delievered
	self.T = threading.Thread(target = self.receiveData)
	self.T.start()
	self.T2 = threading.Thread(target = self.selfConnectedSend)
	self.T2.start()

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
		data = self.soc.recv(self.DATA_SIZE)# receive data whose length <= DATA_SIZE
		print "raw data is : %s" %data
		for realData in data.split("^")[:-1]:
		    self.dataHistory.append(realData)
		    print "data is : %s" %realData
	    except socket.timeout:
		#print "socket timed out"
		continue
	    except:
		print "Connection is lost"
		break
	    
	    self.dataProcessing()
	    #if "info:connList" in data:
		#self.clients = list(data.split(":")[-1])
	    #elif data=='initialize': 
		#self.dataList['cmd'].append( data ) # save the received data
            #else:
                #self.dataList['grid'].append( data)
	self.soc.close() # disconnect the connection
    
    def disconnect(self):
	
	self.endThread = True
	print "joining the thread..."
	self.T.join()
	self.T2.join()
	print "thread is joined"
	pygame.quit()
	sys.exit()
	
    def dataProcessing(self):
	
	# for reading
	for data in self.dataHistory[:]:
	    if "info:connList" in data:
		self.clients = eval(data.split(":")[-1])
		self.lobby(self.clients)
	    elif "info:askPlay" in data:
		self.opponent = data.split(":")[-1].split(";")[0]
		answer = inputbox.ask(self.screen, "'%s' has asked you to play. Accept?(y/n) " %self.opponent)
		if answer in ["Y", "Yes", "y", "yes"]:
		    self.sendData("info:gameAccept:%s;%s" %(self.userName, self.opponent))
		else:
		    self.opponent = None
		    self.waitingForAns = False
		    self.switch = True
	    self.dataHistory.remove(data)
	    self.dataGrave.append(data)    
		    
		    
		
    def selfConnectedSend(self):
	
	# for sending
	# if self.# is changed, send data.
	while not self.endThread:
	    try:
		if self.waitingForAns and self.switch:
		    self.sendData("info:askPlay:%s;%s" %(self.userName, self.waitingForAns))
		    self.switch = False
	    except:
		pass
		
	self.soc.close()

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
    client = bridgeConnection(pygame.display.set_mode((600,600)))
    #client = bridgeConnection(pygame.Surface((600,600)))
    print "now main"
    sleep(3)    
    print "end session"
    client.disconnect()
    
