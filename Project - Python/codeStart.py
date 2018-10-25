#coding: utf-8
''' DÚVIDAS:
    * Os dados de cada cliente deve permanecer na lista caso ele saia?
    * Explicação relacionada aos 'bytes' da mensagem 
    * Todos os 'nicknames' devem ser distintos?
    * Posso indicar mais um comando que representa envio de mensagem ?
    * Teoricamente, classe Chat, o atributo 'self.cliAddr' será idêntico ao atributo 'ip_o' da variável 'message' no método 'receiveData()'
        O que fazer ? 
    * Em relação ao formato da listagem de usuário ( que é feita assim: <NOME, IP, PORTA> )
        Por que imprimir a porta de cada um? 
'''

''' OBS:
    * mudei o comportamendo do comando 'sair()' para:
        * Se 'modo == privado' : sai do modo privado, apenas
        * Se 'modo == chat público' : encerra a sessão do usuário 
    * padrão de formatação:
        * comentários: letras menúsculas
        * avisos do que deve ser feito: LETRAS MAIÚSCULAS
'''

''' COMANDOS ADICIONADOS:
    * enviar(): (client -> server) apenas envia a mensagem. O destino para o qual será enviada depende da variável 'mode' do chat 
    * mostrar(): (server -> client) pede para que o 'cliente' exiba a mensagem 
    * requisicao(): (server -> client) solicita a requisição de privado, considerando para este caso que 'message.msg' representa o 'nickname' do usuário que mandou a mensagem
'''
from socket import *
from threading import Thread
import pickle, sys, random
from classes import *

serverName = '' #Meu IP atual, deve ser verificado sempre
serverPort = 12000

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
serverSocket.bind((serverName,serverPort))

serverSocket.listen(1)

# lista de usuário 
listClients = {}


class Chat(Thread):
    # construtor
    def __init__(self, cliCon, cliAddr, nickname, senha, mode = False):
        Thread.__init__(self)
        self.cliCon = cliCon
        self.cliAddr = cliAddr
        self.nickname = nickname

        self.mode = mode # define se o chat atual é público ou privado
        self.friend = None # usuário que representa o colega do chat privado
        
        if(nickname not in listClients):
            cliCon.sendto("Cadastre-se, informe o seu nickname: ", self.cliAddr)
            nick = cliCon.recv(1024).decode('utf-8')
            # 'False' indica que o usuário não está no privado com ninguém 
            # 'True' indica que o usuário está logado
            listClients[nick] = [cliCon, User(cliAddr, nick, senha)]
            print listClients
        else: 
            listClients[nickname][1].isLogged = True
            listClients[nickname][0] = cliCon
            if listClients[nickname][1].listMessages : # caso tenha mensagens nova para o usuário, envia as mensagens para o mesmo
                self.sendMsg(listClients[nickname][1], listClients[nickname][1].listMessages)
        
        # PERGUNTAR AO PROFESSOR SE SERÁ O 'ServerName' OU O _____não sei kk
        msg = Message(serverName, self.cliAddr, nickname, 'mostrar()', nickname + ' entrou...')

        self.sendMsg(self.nickname, msg)
        Thread(target=self.receiveData).start() # espera por mensagem do usuário 

    def sendMsg(self, name_user, msg):
        if type(msg) is not list: # verifica se há uma lista de mensagens
            msg = [msg]
        if listClients[name_user][1].isLogged:

            #f_string = pickle.dumps(msg)
            map(lambda x: self.cliCon.sendto(pickle.dumps(msg), listClients[name_user][1].cliAddr), msg)
            #self.cliCon.sendto(f_string, listClients[name_user][1].cliAddr)
            #map(lambda x: self.cliCon.sendto(fileObj, user.cliAddr), msg) # sou gay e gosto de rola  TESTAR SE ISSO FUNCIONA (acho que é necessário um 'for')
        else:
            listClients[name_user][1].listMessages += msg
    
    def sendMsgToAll(self, msg):
        for nmC in listClients:
            self.sendMsg(nmC,msg) # SERÁ QUE ESTÁ CERTO?
        
    def receiveData(self):
        while(True):
            message = self.cliCon.recv(1024).decode('utf-8')

            cmd = message.command
            print('Client escreveu: \n', message)

            if cmd == 'lista()':
                listC = ''
                keys = list(listClients.keys())
                for i in range(0, len(listClients)):
                    # gera cada linha da lista a ser enviado ao usuário
                    listC += ('<' + keys[i] + ', ' + listClients[keys[i]][1].cliAddr[0] + ', ' + listClients[keys[i]][1].cliAddr[0] + '>\n')
                self.cliCon.sendto(listC,self.cliAddr)

            # lembrando que para este caso 'message.msg' representa o 'nickname' do usuário que mandou a mensagem
            elif cmd.startswith('privado(') and cmd.endswith(')'): # verifica se o comando é privado(*) M
                # verifica se o 'nickname' existe 
                nick = message.nickname[len('privado('):len(message.nickname)-1]
                if nick in listClients:
                    if not listClients[nick][1].isLogged : # usuário de destinho offline
                        msg = 'mostrar()', 'usuário 'nick + ' está offline!'
                    elif listClients[nick][1].disp :
                        msg = 'usuário 'nick + ' já está no privado com outro usuário!'
                    else:
                        msg = 'solicitação enviada com sucesso!'
                        self.sendMsg(nick, Message(serverName, listClients[nick][1].cliAddr, nick, 'requisicao()', 'usuário ' + message.msg + ' solicitando privado'))
                    # envia mensagem de volva ao usuário solicitante
                    self.sendMsg(message.msg, Message(serverName, self.cliAddr, nick, 'mostrar()', msg))
                    
            elif cmd.startswith('nome(') and cmd.endswith(')'): # verifica se o comando é nome(*)
                new_nickname = message.nickname[len('nome('):len(message.nickname)-1]
                self.sendMsg(listClients[message.ip_o].nickname + ' agora é ' + new_nickname)
                listClients[message.ip_o].nickname = message.nickname[len('nome('):len(message.nickname)-1]
                
            elif cmd == 'sair()':
                if self.mode : # verifica se o chat é privado 
                    listClients[message.ip_o].disp = False
                    self.mode = False
                else :
                    listClients[message.ip_o].isLogged = False
                    self.sendMsg(listClients[message.ip_o].nickname + 'saiu!')
                    self.cliCon.close()
                    break
            elif cmd == 'enviar()':
                if self.mode : # verifica se o chat é privado 
                    # CONFIGURAR MENSAGEM ANTES DE ENVIAR 
                    self.sendMsg(listClients[self.cliAddr], message) 
                else:
                    # CONFIGURAR MENSAGEM ANTES DE ENVIAR 
                    self.sendMsgToAll(message)
            else:
                self.sendMsg('comando inválido!\n')

while 1:
    print('The server has started... \n')
    cliCon, cliAddr = serverSocket.accept()
    # False: chat público (padrão)
    # True: chat privado 
    print('... usuário fazendo login ...')

    # FAZER LOGIN DO USUÁRIO AQUI 

    nickname, senha = 'higor' + str(random.choice('asdfghqwerzxcvçlkiuo')), '12345' # para fins de teste
    Chat(cliCon, cliAddr, nickname, senha).start()
