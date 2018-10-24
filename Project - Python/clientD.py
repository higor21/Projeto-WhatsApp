from socket import * 
from threading import Thread
import time


ip_server = '127.0.0.1' # IP of server to connect
serverPort = 12000 # port to connect
clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((ip_server,serverPort))

print 'asdflajdslk'

def getMessage():
	while 1:
		message = clientSocket.recv(1024)
		print "\nMessage received by server: %s" % message
		time.sleep(1) #sleep by 1ms


#start here!
print 'Client started!\n'
Thread(target=getMessage, args=()).start();
while 1:
	sentence = raw_input('Input the command: ')
	clientSocket.send(sentence)
	