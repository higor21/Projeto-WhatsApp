#coding: utf-8
from socket import * 
from threading import Thread
import time, pickle
from classes import *
from queue import *
from os import system

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
answer = ''
isPrivate = False

def getMessage():
	global listUserNames
	while True:
		bitStream = clientSocket.recv(1024)
		if answer != 'sair()':
			message = Message(bitstream = bitStream)

			# print('-> ' + str(ask.command) + ' : ' + ask.nickname)
			
			if message.command == cmd_.ATUALIZAR and message.nickname not in listUserNames:
				listUserNames.append(message.nickname)

			if message.command == cmd_.LISTA_USERS:
				listUserNames = list(message.msg.split(';'))

			else:
				if message.command not in [cmd_.MOSTRAR, cmd_.ATUALIZAR]:
					listMessages.put(message)
				else:
					print('\n' + (message.nickname.replace(' ','') + ' escreveu: ' if message.nickname.replace(' ','') != my_nick.replace(' ','') else '') + str(message.msg) + '\n')
		else :
			break

def printM():
	global cmd, ask
	while True: 
		if not listMessages.empty() and not cmd and answer != 'sair()':
			ask = listMessages.get()
			print(ask.msg)
			cmd = True
		elif answer == 'sair()':
			break


#start here!
print ('Client started!\n')
Thread(target=getMessage, args=()).start()
Thread(target=printM, args=()).start()

while True:
	cmd = False
	nick , msg, command = '------', '', cmd_.CMD_PADRAO
	command = int(cmd_.CMD_PADRAO)
	answer = input('\n' + my_nick + (': ' if my_nick != '' else '')) # espera por um comando
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
			elif ask.command == cmd_.LOG_REG or ask.command == cmd_.REQUISITO:
				if answer.upper() not in ['Y', 'N']:
					print("Digite um caractere apenas, podendo ser y,Y,n,N")
				else:
					accept = True
					msg = answer.upper()
					nick = ask.nickname
					command = cmd_.RESPOSTA
			elif ask.command == cmd_.SAIR:
				accept = True

			if not accept:		
				answer = input(ask.msg)
			else : 
				break
	else :
		if answer in ['lista()','sair()']:
			nick = my_nick
			command = ( cmd_.LISTA if answer == 'lista()' else cmd_.SAIR )
			if answer == 'sair()':
				clientSocket.send(bytes(Message(clientSocket.getsockname()[0],ip_server,nick,command,msg)))
		elif (answer.startswith('privado(') and answer.endswith(')')) or (answer.startswith('nome(') and answer.endswith(')')):
			inicio_cmd = (True if answer[0] == 'p' else False)
			nick = answer[len('privado(' if inicio_cmd else 'nome('): len(answer) - 1] 
			nick = (nick + (6 - len(nick))*' ')
			if nick != my_nick:
				if ((nick in listUserNames) if inicio_cmd else (nick not in listUserNames)):
					my_nick = (my_nick if inicio_cmd else nick)
					command = (cmd_.PRIVADO if inicio_cmd else cmd_.CG_NOME)
					isPrivate = inicio_cmd
				else:
					print('\n' + ('Não' if inicio_cmd else 'Já') + ' existe usuários com este nome')
					continue
			else:
				print('\n ' + nick + ' é seu nome, digite outro nome \n')
				continue
		else:
			msg = answer
			nick = my_nick
			command = cmd_.ENVIAR
	
	if ask.command == cmd_.SAIR or (command == cmd_.SAIR and not isPrivate):
		system('clear')
		print('\n\nvocê optou por sair!')
		break

	clientSocket.send(bytes(Message(clientSocket.getsockname()[0],ip_server,nick,command,msg)))