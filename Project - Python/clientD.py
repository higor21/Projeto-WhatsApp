#coding: utf-8
from socket import * 
from threading import Thread
import time, pickle
from classes import *

ip_server = '192.168.0.9' # IP of server to connect
serverPort = 12000 # port to connect
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((ip_server,serverPort))

def getMessage():
	while 1:
		message = clientSocket.recv(1024)
		s = '\n------ Mensagem do servidor ------\n' + str(pickle.loads(message))
		print(s + '\n----------------------------------\n')
		time.sleep(1)


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
	