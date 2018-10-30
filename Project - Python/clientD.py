#coding: utf-8
from socket import * 
from threading import Thread
import time, pickle
from classes import *
from queue import *

ip_server = '127.0.0.1' # IP of server to connect
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
		bitStream = clientSocket.recv(1024)
		message = Message(bitstream = bitStream)

		if message.command != cmd_.MOSTRAR:
			listMessages.put(message)
		else:
			s = '\n------ Mensagem do servidor ------\n' + str(message.msg)
			print(s + '\n----------------------------------\n')

def printM():
	global cmd, ask
	while True: 
		if not listMessages.empty() and not cmd:
			ask = listMessages.get()
			print(ask)
			cmd = True

#start here!
print ('Client started!\n')
Thread(target=getMessage, args=()).start()
Thread(target=printM, args=()).start()

while True:
	cmd = False
	nick , msg, command = '------', '', cmd_.CMD_PADRAO
	command = int(cmd_.CMD_PADRAO)
	answer = input() # espera por um comando
	if cmd:
		while True:
			accept = False
			if ask.command == cmd_.ACESSAR : 
				if list(answer).count('|') != 1 or answer.startswith('|') or answer.endswith('|') or len(answer.split('|')[0]) > 6:
					print('nickname ou senha inválidos!\nInforme-os novamente')
				else :
					my_nick = answer.split('|')[0] # nickname do usuário
					msg = answer
					accept = True
			elif ask.command == cmd_.LOG_CAD :
				if answer.upper() not in ['C', 'L']:
					print("Digite um caractere apenas, podendo ser c,C,l,L")
				else:
					accept = True
					msg = answer.upper()
			elif ask.command == cmd_.LOG_REG or ask.command == 'requisicao()':
				if answer.upper() not in ['Y', 'N']:
					print("Digite um caractere apenas, podendo ser y,Y,n,N")
				accept = True
				msg = answer.upper()
				nick = ask.nickname
				command = cmd_.RESPOSTA
			if not accept:		
				answer = input(ask.msg)
			else : 
				break
	else :
		if answer in ['lista()','sair()']:
			nick = my_nick
			command = ( cmd_.LISTA if answer == 'lista()' else cmd_.SAIR )
		elif (answer.startswith('privado(') and answer.endswith(')')) or (answer.startswith('name(') and answer.endswith(')')):
			inicio_cmd = (True if answer[0] == 'p' else False)
			nick = answer[len('privado(' if inicio_cmd else 'name('): len(answer) - 1] # não precisava
			command = (cmd_.PRIVADO if inicio_cmd else cmd_.CG_NOME)
		else:
			msg = answer
			nick = my_nick
			command = cmd_.ENVIAR
	
	print(type(command))
	clientSocket.send(bytes(Message(clientSocket.getsockname()[0],ip_server,nick,command,msg)))
	
