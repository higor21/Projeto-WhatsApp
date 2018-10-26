#coding: utf-8
from socket import * 
from threading import Thread
import time, pickle
from classes import *

ip_server = '' # IP of server to connect
serverPort = 12000 # port to connect
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((ip_server,serverPort))

def getMessage():
	while 1:
		message = clientSocket.recv(1024)
		print('\n------ Mensagem do servidor ------\n')
		print (pickle.loads(message))
		print('\n----------------------------------\n')
		time.sleep(1) #sleep by 1ms


#start here!
print ('Client started!\n')
Thread(target=getMessage, args=()).start()
time.sleep(1)
while 1:
	cmd = raw_input('Input the command: ')
	nick = raw_input('Input the nick: ')
	msg = raw_input('Input the msg: ')
	msg = Message(clientSocket.getsockname(),(ip_server,serverPort),nick,cmd,msg)
	print(msg)
	clientSocket.send(pickle.dumps(msg))
	