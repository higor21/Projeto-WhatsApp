#coding: utf-8
from socket import * 
from threading import Thread
import time, pickle, classes

ip_server = '' # IP of server to connect
serverPort = 12000 # port to connect
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((ip_server,serverPort))

def getMessage():
	while 1:
		message = clientSocket.recv(1024)
		print (pickle.loads(message).msg.decode('utf-8'))
		time.sleep(1) #sleep by 1ms


#start here!
print ('Client started!\n')
Thread(target=getMessage, args=()).start();
while 1:
	cmd = raw_input('Input the command: ')
	nick = raw_input('Input the nick: ')
	msg = raw_input('Input the msg: ')
	clientSocket.send(pickle.dumps(classes.Message(clientSocket.getsockname(),(ip_server,serverPort),nick,cmd,msg)))
	