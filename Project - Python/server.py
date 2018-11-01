#coding: utf-8

'''
    * fazer cliente saber de onde veio a mensagem
    * previnir que dois usuários logem na mesma conta ao mesmo tempo
    * fazer classe de conversão para bytes
'''

from socket import *
from threading import Thread
import pickle, sys, random, time
from classes import *
from functools import reduce

serverName = '127.0.0.1'  # Meu IP atual, deve ser verificado sempre
serverPort = 12000

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverName, serverPort))

serverSocket.listen(1)

# lista de usuário 
listClients = {}
# lista de privados
listPrivates = {}

def serverShell():
    while (True):
        cmd = input()
        if cmd == 'lista()':
            # imprime a lista de todos os usuários 
            listAll = map(lambda x: '<' + x +', ' +  str(listClients[x][0].getsockname()[0]) + ', ' + str(listClients[x][0].getsockname()[1]) + '>'  + (' (privado)' if x in listPrivates else '') ,listClients.keys())
            print('\n'.join(list(listAll)))
        elif cmd == 'sair()':
            map(lambda x: listClients[x][0].close() ,listClients.keys())
            #map(lambda x: sendMsgToAll(x[1].nickname + 'saiu!') ,listClients.values())
            for x in listClients.values():
                x[1].isLogged = False
            msg = Message(ip_src = serverName, command = cmd_.SAIR, msg = 'saindo')
            for nick in listClients.keys():
                if listClients[nick][1].isLogged:
                    print('-> ' + nick)
                    msg.ip_dest = listClients[nick][1].cliAddr[0]
                    msg.nickname = nick
                    listClients[nick][0].sendto(bytes(msg), listClients[nick][1].cliAddr)

# login do usuário
class Access():
    def __init__(self, cliCon, cliAddr, mode = 'L'):
        self.cliCon, self.cliAddr, self.mode = cliCon, cliAddr, mode
        #pede 'nickname' e 'password' do usuário
        cliCon.sendto(bytes(Message(serverName, cliAddr[0], 'nicknm', cmd_.ACESSAR ,"\nnickname|password: ")), cliAddr)
        self.dados = Message(bitstream = cliCon.recv(1024)).msg.split('|')
        self.dados[0] += (6 - len(self.dados[0]))*' '
        self.login() if mode == 'L' else self.register() # operador ternário do python
        if self.dados != None:
            self.dados[0] += (6 - len(self.dados[0]))*' '
            listClients[self.dados[0]] = [cliCon, User(self.cliAddr, self.dados[0]), self.dados[1]]

    def login(self):
        if (self.dados[0] not in listClients or listClients[self.dados[0]][2] != self.dados[1]):
            # mensagem informando dados inválidos
            msg = Message(serverName, cliAddr[0], self.dados[0], cmd_.LOG_REG,"nickname ou password inválido(s)!\n\t* Y: tentar novamente\n\t* N: se cadastrar")
            self.cliCon.sendto(bytes(msg), self.cliAddr)
            resp = Message(bitstream = self.cliCon.recv(1024)).msg.upper()
            self.__init__(self.cliCon, self.cliAddr, 'L' if resp == 'Y' else 'C')
        return self.dados # pode logar 

    def register(self):
        if (self.dados[0] in listClients):
            # mensagem informando dados inválidos
            msg = Message(serverName, cliAddr[0], self.dados[0], cmd_.LOG_REG ,"nickname já existe!\n\t* Y: tentar novamente\n\t* N: sair")
            self.cliCon.sendto(bytes(msg), self.cliAddr)
            if Message(bitstream = self.cliCon.recv(1024)).msg.upper() == 'Y':
                self.__init__(self.cliCon, self.cliAddr, 'C')
            return None # não pode logar 
        return self.dados # pode logar 
    

class Chat(Thread):
    def __init__(self, cliCon, cliAddr, nickname):
        """Construtor"""
        Thread.__init__(self)
        self.cliCon, self.cliAddr, self.nickname = cliCon, cliAddr, nickname
        listClients[self.nickname][1].isLogged = True
        listClients[self.nickname][0] = cliCon
        # caso tenha mensagens nova para o usuário, envia as mensagens para o mesmo
        while listClients[self.nickname][1].listMessages:
            self.sendMsg(self.nickname, listClients[self.nickname][1].listMessages.pop())
            time.sleep(0.1)

        # avisa que o usuároi 'nickname' entrou para todas as pessoas
        self.sendMsgToAll(Message(serverName, self.cliAddr[0], nickname, cmd_.ATUALIZAR, 'eu entrei...'))

        msg = Message(serverName,listClients[self.nickname][1].cliAddr[0], self.nickname, cmd_.LISTA_USERS, reduce(lambda x,y: x + ';' + y ,listClients.keys()))
        self.sendMsg(self.nickname, msg)

        Thread(target=self.receiveData).start()  # espera por mensagem do usuário 
    
    def sendMsg(self, user_name, msg):
        """Função para administrar o envio de mensagens do Servidor"""
        if type(msg) is not list:  # verifica se há uma lista de mensagens
            msg = [msg]

        if user_name in listClients.keys() :
            if listClients[user_name][1].isLogged:
                #Se o cliente está logado, envia as mensagens
                #map(lambda x: listClients[user_name][0].sendto(bytes(x), listClients[user_name][1].cliAddr), msg)
                for i in range(0, len(msg)):
                    msg[i].nickname = self.nickname + (6 - len(self.nickname))*' '
                    listClients[user_name][0].sendto(bytes(msg[i]), listClients[user_name][1].cliAddr)

            else:
                #Se o cliente não está logado, acumula as mensagens para enviar quando este logar
                listClients[user_name][1].listMessages += msg

    def sendMsgToAll(self, msg):
        """Função para enviar mensagens para TODOS os usuários"""
        for x in listClients.keys():
            if x != self.nickname and x not in listPrivates.keys():
                self.sendMsg(x, msg)

    def receiveData(self):
        while (listClients[self.nickname][1].isLogged):
            
            message = Message(bitstream = self.cliCon.recv(1024))

            cmd = message.command
            if self.nickname not in listPrivates and message.command == cmd_.ENVIAR: # apenas assim mostra no servidor
                print( self.nickname + ' escreveu: ', message.msg)

            if cmd == cmd_.LISTA:
                logged_list = ''
                keys = list(listClients.keys())
                for i in range(0, len(listClients)):
                    # gera cada linha da lista a ser enviado ao usuário
                    logged_list += ('<' + keys[i] +', ' + str(self.cliCon.getsockname()[0]) + ', ' + str(self.cliCon.getsockname()[1]) + '> ' + ('(privado)' if keys[i] in listPrivates else '') + '\n') #Esta é a porta mesmo?
                msg = Message(serverName, self.cliAddr[0], self.nickname, cmd_.MOSTRAR, logged_list)
                self.cliCon.sendto(bytes(msg), self.cliAddr)

            elif cmd == cmd_.PRIVADO:  # verifica se o comando é privado(*) M
                nick = message.nickname
                # verifica se o 'nickname' existe
                if nick in listClients:
                    if not listClients[nick][1].isLogged:  # usuário de destinho offline
                        msg = 'usuário ' + nick + ' está offline!'
                    elif nick in listPrivates:  # verifica se ele está no privado com alguém
                        msg = 'usuário ' + nick + ' já está no privado com outro usuário!'
                    else:
                        msg = 'solicitação enviada com sucesso!'
                        self.sendMsg(nick, Message(serverName, listClients[nick][1].cliAddr[0], self.nickname, cmd_.REQUISITO, 'usuário ' + self.nickname + ' solicitando privado'))
                    # envia mensagem de volta ao usuário solicitante
                    self.sendMsg(self.nickname, Message(serverName, self.cliAddr[0], self.nickname, cmd_.MOSTRAR, msg))

            # para este caso, o 'nickname' enviado é o do próprio usuário, visto que ele quer trocar seu próprio nome
            elif cmd == cmd_.CG_NOME:  # verifica se o comando é nome(*)
                if message.nickname not in listClients.keys():
                    new_nickname = message.nickname # pega o novo 'nickname'
                    msg = self.nickname + ' agora é ' + new_nickname
                    listClients[new_nickname] = listClients.pop(self.nickname)  # trocando o nome do usuário
                    self.nickname = new_nickname
                    self.sendMsgToAll(Message(serverName, listClients[new_nickname][1].cliAddr[0], new_nickname, cmd_.MOSTRAR, msg))

            # para este caso, o 'nickname' enviado é o do próprio usuário, visto que ele quer sair da conversa (privada/chat)
            elif cmd == cmd_.SAIR:
                if self.nickname in listPrivates:  # verifica se o chat é privado
                    msg = Message(serverName, listClients[listPrivates[self.nickname]][1].cliAddr[0],
                        listPrivates[self.nickname], cmd_.MOSTRAR,
                        'usuário ' + self.nickname + ' cancelou o privado!')
                    # avisa para o colega que o chat privado foi desconectado, visto que o outro cancelou
                    self.sendMsg(listPrivates[self.nickname], msg)
                    listPrivates.pop(listPrivates[self.nickname])  # remove o amigo do privado
                    listPrivates.pop(self.nickname)  # remove o mesmo do privado
                else:
                    listClients[self.nickname][1].isLogged = False
                    msg = Message(serverName, listClients[self.nickname][1].cliAddr[0], self.nickname, cmd_.MOSTRAR, listClients[self.nickname][1].nickname + ' saiu!')
                    self.sendMsgToAll(msg)
                    listClients[self.nickname][0].close()
                    break  # sai da Thread
            # 'message.nickname' representa para onde quero enviar 
            elif cmd == cmd_.ENVIAR:
                #if message.nickname == listPrivates[self.nickname]:  # verifica se o chat é privado
                if self.nickname in listPrivates :
                    self.sendMsg(listPrivates[self.nickname], Message(serverName, listClients[self.nickname][1].cliAddr[0], listClients[self.nickname][1].nickname, cmd_.MOSTRAR, message.msg))
                else:
                    msg = message
                    msg.command = cmd_.MOSTRAR
                    self.sendMsgToAll(msg)

            elif cmd == cmd_.RESPOSTA:
                # adicionando a relação entre os usuários
                if message.msg == 'Y' : 
                    listPrivates[self.nickname] = message.nickname
                    listPrivates[message.nickname] = self.nickname
                    self.sendMsg(self.nickname,
                        Message(serverName, listClients[self.nickname][1].cliAddr[0], self.nickname, cmd_.MOSTRAR, 'você e ' + message.nickname + ' estão agora no privado'))
                    self.sendMsg(message.nickname,
                        Message(serverName, listClients[message.nickname][1].cliAddr[0], message.nickname, cmd_.MOSTRAR, 'você e ' + self.nickname + ' estão agora no privado'))
                else :
                    self.sendMsg(self.nickname,
                        Message(serverName, listClients[self.nickname][1].cliAddr[0], self.nickname, cmd_.MOSTRAR, message.nickname + ' não aceitou a solicitação de privado'))

            else:
                self.sendMsg(self.nickname, Message(serverName, listClients[self.nickname][1].cliAddr[0], self.nickname, cmd_.MOSTRAR,'comando inválido!'))

def login(cliCon, cliAddr):
    cliCon.sendto(bytes(Message(serverName, cliAddr[0], 'nick', cmd_.LOG_CAD, "\nInforme:\n\t* L: login\n\t* C: cadastro\n")), cliAddr)
    
    resp = Access(cliCon, cliAddr, Message(bitstream = cliCon.recv(1024)).msg.upper())
    
    if resp.dados != None:
        Chat(cliCon, cliAddr, resp.dados[0]).start()


print('The server has started... \n')
Thread(target=serverShell).start()
while 1:
    cliCon, cliAddr = serverSocket.accept()
    
    print('... usuário fazendo login ...')
    Thread(target=login, args=(cliCon, cliAddr)).start()