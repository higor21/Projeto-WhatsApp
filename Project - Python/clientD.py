#coding: utf-8
from socket import * 
from threading import Thread
import time, pickle
from classes import *
from Queue import *

ip_server = '192.168.0.9' # IP of server to connect
serverPort = 12000 # port to connect
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((ip_server,serverPort))

# fila de mensagens a ser respondidas
listMessages = Queue()

# lista de usuários
listUserNames = []

cmd = False
ask = Message()
my_nick = ''

def getMessage():
	while True:
		message = pickle.loads(clientSocket.recv(1024))

		if message.command != 'mostrar()':
			listMessages.put(message)
		else:
			s = '\n------ Mensagem do servidor ------\n' + str(message.msg)
			print(s + '\n----------------------------------\n')

def printM():
	global cmd, ask
	while True: 
		if not listMessages.empty() and not cmd:
			ask = listMessages.get()
			print(ask.msg)
			cmd = True

#start here!
print ('Client started!\n')
Thread(target=getMessage, args=()).start()
Thread(target=printM, args=()).start()

while True:
	cmd = False
	nick , msg, command = '', '', ''
	answer = raw_input() # espera por um comando
	if cmd:
		while True:
			accept = False
			if ask.command == 'access()' : 
				if list(answer).count('|') != 1 or answer.startswith('|') or answer.endswith('|'):
					print('nickname ou senha inválidos!\nInforme-os novamente')
				else :
					my_nick = answer.split('|')[0] # nickname do usuário
					msg = answer
					accept = True
			elif ask.command == 'log_cad()':
				if answer.upper() not in ['C', 'L']:
					print("Digite um caractere apenas, podendo ser c,C,l,L")
				else:
					accept = True
					msg = answer.upper()
			elif ask.command == 'log_reg()' or ask.command == 'requisicao()':
				if answer.upper() not in ['Y', 'N']:
					print("Digite um caractere apenas, podendo ser y,Y,n,N")
				accept = True
				msg = answer.upper()
				command = 'resposta()'
			if not accept:		
				answer = raw_input(ask.msg)
			else : 
				break
	else :
		if answer in ['lista()','sair()']:
			nick = my_nick
			command = answer
		elif (answer.startswith('privado(') and answer.endswith(')')) or (answer.startswith('name(') and answer.endswith(')')):
			nick = answer[len('privado('): len(answer) - 1] # não precisava
			command = answer
		else:
			msg = answer
			nick = my_nick
			command = 'enviar()'
	print(nick + ' , ' + command + ' , ' + msg)
	clientSocket.send(pickle.dumps(Message(clientSocket.getsockname(),(ip_server,serverPort),nick,command,msg)))
	