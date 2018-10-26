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
    * enviar(): (client -> server) apenas envia a mensagem. O destino para o qual será enviada depende do chat (se é privado ou não)
    * mostrar(): (server -> client) pede para que o 'cliente' exiba a mensagem 
    * requisicao(): (server -> client) solicita a requisição de privado, considerando para este caso que 'message.msg' representa o 'nickname' do usuário que mandou a mensagem
    * resposta(): (client -> server) resposta em relação a requisição feita antes
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
# relação de privados
listPrivates = {}

class Chat(Thread):
    # construtor
    def __init__(self, cliCon, cliAddr, nickname, senha):
        Thread.__init__(self)
        self.cliCon = cliCon
        self.cliAddr = cliAddr
        self.nickname = nickname
        
        if(nickname not in listClients):
            cliCon.sendto("Cadastre-se, informe o seu nickname: ", self.cliAddr)
            nick = cliCon.recv(1024).decode('utf-8')
            # 'False' indica que o usuário não está no privado com ninguém 
            # 'True' indica que o usuário está logado
            listClients[nick] = [cliCon, User(cliAddr, nick, senha)]
            print listClients[nick][1]
        else: 
            listClients[nickname][1].isLogged = True
            listClients[nickname][0] = cliCon
            if listClients[nickname][1].listMessages : # caso tenha mensagens nova para o usuário, envia as mensagens para o mesmo
                self.sendMsg(nickname, listClients[nickname][1].listMessages)
        
        msg = Message(serverName, self.cliAddr, nickname, 'mostrar()', nickname + ' entrou...')

        self.sendMsg(self.nickname, msg)

        Thread(target=self.receiveData).start() # espera por mensagem do usuário 

    def sendMsg(self, name_user, msg):
        if type(msg) is not list: # verifica se há uma lista de mensagens
            msg = [msg]
        print(type(msg[0]))
        if listClients[name_user][1].isLogged:

            #f_string = pickle.dumps(msg)
            map(lambda x: self.cliCon.sendto(pickle.dumps(x), listClients[name_user][1].cliAddr), msg)
            #self.cliCon.sendto(f_string, listClients[name_user][1].cliAddr)
            #map(lambda x: self.cliCon.sendto(fileObj, user.cliAddr), msg) # sou gay e gosto de rola  TESTAR SE ISSO FUNCIONA (acho que é necessário um 'for')
        else:
            listClients[name_user][1].listMessages += msg
    
    def sendMsgToAll(self, msg):
        for nmC in listClients:
            self.sendMsg(nmC,msg) # SERÁ QUE ESTÁ CERTO?
        
    def receiveData(self):
        while(True):
            message = self.cliCon.recv(1024)
            message = pickle.loads(message)
            cmd = message.command
            print('Client escreveu: \n', message)

            if cmd == 'lista()':
                listC = ''
                keys = list(listClients.keys())
                for i in range(0, len(listClients)):
                    # gera cada linha da lista a ser enviado ao usuário
                    listC += ('<' + keys[i] + ', ' + listClients[keys[i]][1].cliAddr[0] + ', ' + listClients[keys[i]][1].cliAddr[0] + '>\n')
                self.cliCon.sendto(listC,self.cliAddr)

            # lembrando: que para este caso 'message.nickname' representa o 'nickname' do usuário que mandou a mensagem
            elif cmd.startswith('privado(') and cmd.endswith(')'): # verifica se o comando é privado(*) M
                # verifica se o 'nickname' existe 
                nick = cmd[len('privado('):len(message.nickname)-1]
                if nick in listClients:
                    if not listClients[nick][1].isLogged : # usuário de destinho offline
                        msg = 'mostrar()', 'usuário '+ nick + ' está offline!'
                    elif nick in listPrivates: # verifica se ele está no privado com alguém
                        msg = 'usuário ' + nick + ' já está no privado com outro usuário!'
                    else:
                        msg = 'solicitação enviada com sucesso!'
                        self.sendMsg(nick, Message(serverName, listClients[nick][1].cliAddr, nick, 'requisicao()', 'usuário ' + message.msg + ' solicitando privado'))
                    # envia mensagem de volva ao usuário solicitante
                    self.sendMsg(message.nickname, Message(serverName, self.cliAddr, nick, 'mostrar()', msg))
            
            # para este caso, o 'nickname' enviado é o do próprio usuário, visto que ele quer trocar seu próprio nome
            elif cmd.startswith('nome(') and cmd.endswith(')'): # verifica se o comando é nome(*)
                new_nickname = message.nickname[len('nome('):len(message.nickname)-1] # pega o novo 'nickname'
                msg = message.nickname + ' agora é ' + new_nickname
                listClients[new_nickname] = listClients.pop(message.nickname) # trocando o nome do usuário 
                self.sendMsg(new_nickname, Message(serverName, listClients[new_nickname][1].cliAddr, new_nickname, 'mostrar()', msg))
            
            # para este caso, o 'nickname' enviado é o do próprio usuário, visto que ele quer sair da conversa (privada/chat)
            elif cmd == 'sair()':
                if message.nickname in listPrivates : # verifica se o chat é privado 
                    msg = Message(serverName, listClients[listPrivates[message.nickname]][1].cliAddr, listPrivates[message.nickname], 'mostrar()','usuário ' + message.nickname + ' cancelou o privado!')
                    # avisa para o colega que o chat privado foi desconectado, visto que o outro cancelou
                    self.sendMsg(listPrivates[message.nickname], msg) 
                    listPrivates.pop(listPrivates[message.nickname]) # remove o amigo do privado
                    listPrivates.pop(message.nickname) # remove o mesmo do privado
                else :
                    listClients[message.nickname].isLogged = False
                    self.sendMsgToAll(listClients[message.nickname][1].nickname + 'saiu!')
                    listClients[message.nickname][1].cliCon.close()
                    break # sai da Thread
            elif cmd == 'enviar()':
                if message.nickname in listPrivates : # verifica se o chat é privado 
                    self.sendMsg(listClients[message.nickname], Message(serverName, listPrivates[message.nickname][1].cliAddr, message.nickname, 'mostrar()',message.msg)) 
                else:
                    self.sendMsgToAll(Message(message.msg))
            elif cmd == 'resposta()':
                # adicionando a relação entre os usuários 
                listPrivates[self.nickname] = message.nickname
                listPrivates[message.nickname] = self.nickname
                self.sendMsg(self.nickname, Message(serverName, listClients[self.nickname][1].cliAddr, self.nickname, 'mostrar()', 'você e ' + message.nickname + ' estão agora no privado'))
                self.sendMsg(message.nickname, Message(serverName, listClients[message.nickname][1].cliAddr, message.nickname, 'mostrar()', 'você e ' + self.nickname + ' estão agora no privado'))
            else: 
                self.sendMsg(self.nickname, Message(serverName, listClients[self.nickname][1].cliAddr, self.nickname, 'mostrar()', 'comando inválido!'))

while 1:
    print('The server has started... \n')
    cliCon, cliAddr = serverSocket.accept()
    # False: chat público (padrão)
    # True: chat privado 
    print('... usuário fazendo login ...')

    # FAZER LOGIN DO USUÁRIO AQUI 

    nickname, senha = 'higor' + str(random.choice('asdfghqwerzxcvçlkiuo')), '12345' # para fins de teste
    Chat(cliCon, cliAddr, nickname, senha).start()
