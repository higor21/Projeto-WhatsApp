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
    * Um usuário pode enviar mensagem para outro em específico, sem que seja solicitado um PRIVADO a tal pessoa?
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

serverName = ''  # Meu IP atual, deve ser verificado sempre
serverPort = 12000

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverName, serverPort))

serverSocket.listen(1)

# lista de usuário 
listClients = {}
# lista de privados
listPrivates = {}

# login do usuário
class Access():
    def __init__(self, cliCon, cliAddr, mode = 'L'):
        self.cliCon, self.cliAddr, self.mode = cliCon, cliAddr, mode
        #pede 'nickname' e 'password' do usuário
        msg = Message(serverName, cliAddr, 'nickname', 'mostrar()',"\nnickname|password: ")
        cliCon.sendto(pickle.dumps(msg), cliAddr)
        self.dados = pickle.loads(cliCon.recv(1024)).msg.split('|')
        self.login() if mode == 'L' else self.register() # operador ternário do python
        if self.dados != None:
            listClients[self.dados[0]] = [cliCon, User(self.cliAddr, self.dados[0]), self.dados[1]]

    def login(self):
        if (self.dados[0] not in listClients or listClients[self.dados[0]][2] != self.dados[1]):
            # mensagem informando dados inválidos
            msg = Message(serverName, cliAddr, self.dados[0],
            'mostrar()',"nickname ou password inválido(s)!\n\t* Y: tentar novamente\n\t* N: se cadastrar")
            cliCon.sendto(pickle.dumps(msg), self.cliAddr)
            if pickle.loads(cliCon.recv(1024)).msg.upper() == 'Y':
                self.__init__(self.cliCon, self.cliAddr, 'L')
            return None # não pode logar 
        return self.dados # pode logar 

    def register(self):
        if (self.dados[0] in listClients):
            # mensagem informando dados inválidos
            msg = Message(serverName, cliAddr, self.dados[0],
            'mostrar()',"nickname já existe!\n\t* Y: tentar novamente\n\t* N: sair")
            cliCon.sendto(pickle.dumps(msg), self.cliAddr)
            if pickle.loads(cliCon.recv(1024)).msg.upper() == 'Y':
                self.__init__(self.cliCon, self.cliAddr, 'C')
            return None # não pode logar 
        return self.dados # pode logar 
    

class Chat(Thread):
    def __init__(self, cliCon, cliAddr, nickname):
        """Construtor"""
        Thread.__init__(self)
        self.cliCon, self.cliAddr, self.nickname = cliCon, cliAddr, nickname
        print('dfasdfasdf1')
        listClients[self.nickname][1].isLogged = True
        listClients[self.nickname][0] = cliCon
        # caso tenha mensagens nova para o usuário, envia as mensagens para o mesmo
        if listClients[self.nickname][1].listMessages:
            map(lambda x: self.sendMsg(self.nickname, x), listClients[self.nickname][1].listMessages)
        print('dfasdfasdf2')
        # avisa que o usuároi 'nickname' entrou para todas as pessoas
        msg = Message(serverName, self.cliAddr, nickname, 'mostrar()', nickname + ' entrou...')
        self.sendMsgToAll(msg)
        print('dfasdfasdf3')
        print(msg)

        Thread(target=self.receiveData).start()  # espera por mensagem do usuário 

    def sendMsg(self, user_name, msg):
        """Função para administrar o envio de mensagens do Servidor"""
        if type(msg) is not list:  # verifica se há uma lista de mensagens
            msg = [msg]
        
        if user_name in listClients :
            if listClients[user_name][1].isLogged:
                #Se o cliente está logado, envia as mensagens
                #pickle.dumps() converte uma mensagem string em bytestream
                map(lambda x: listClients[user_name][0].sendto(pickle.dumps(x), listClients[user_name][1].cliAddr), msg)
                # self.cliCon.sendto(f_string, listClients[user_name][1].cliAddr)
                # map(lambda x: self.cliCon.sendto(fileObj, user.cliAddr), msg)
            else:
                #Se o cliente não está logado, acumula as mensagens para enviar quando este logar
                listClients[user_name][1].listMessages += msg
        else : 
            pass # TRATAR ISSO DEPOIS

    def sendMsgToAll(self, msg):
        """Função para enviar mensagens para TODOS os usuários"""
        for nmC in listClients:
            if nmC != self.nickname :
                self.sendMsg(nmC, msg)

    def receiveData(self):
        while (True):
            
            message = self.cliCon.recv(1024)
            message = pickle.loads(message)
            cmd = message.command
            print( message.nickname + ' escreveu: ', message.msg)

            if cmd == 'lista()':
                logged_list = ''
                keys = list(listClients.keys())
                for i in range(0, len(listClients)):
                    # gera cada linha da lista a ser enviado ao usuário
                    logged_list += ('<' + keys[i] + ', ' + self.cliCon.getsockname[0] + ', ' +
                              self.cliCon.getsockname[1] + '>\n') #Esta é a porta mesmo?
                msg = Message(serverName, self.cliAddr, self.nickname, 'mostrar()', logged_list)
                self.cliCon.sendto(pickle.dumps(msg), self.cliAddr)

            elif cmd.startswith('privado(') and cmd.endswith(')'):  # verifica se o comando é privado(*) M
                nick = cmd[len('privado('):len(cmd) - 1]
                # verifica se o 'nickname' existe
                if nick in listClients:
                    if not listClients[nick][1].isLogged:  # usuário de destinho offline
                        msg = 'mostrar()', 'usuário ' + nick + ' está offline!'
                    elif nick in listPrivates:  # verifica se ele está no privado com alguém
                        msg = 'usuário ' + nick + ' já está no privado com outro usuário!'
                    else:
                        msg = 'solicitação enviada com sucesso!'
                        print(nick)
                        self.sendMsg(nick, Message(serverName, listClients[nick][1].cliAddr, nick, 'requisicao()',
                                                   'usuário ' + self.nickname + ' solicitando privado'))
                    # envia mensagem de volta ao usuário solicitante
                    self.sendMsg(self.nickname, Message(serverName, self.cliAddr, self.nickname, 'mostrar()', msg))

            # para este caso, o 'nickname' enviado é o do próprio usuário, visto que ele quer trocar seu próprio nome
            elif cmd.startswith('nome(') and cmd.endswith(')'):  # verifica se o comando é nome(*)
                new_nickname = cmd[len('nome('):len(cmd) - 1]  # pega o novo 'nickname'
                msg = self.nickname + ' agora é ' + new_nickname
                listClients[new_nickname] = listClients.pop(self.nickname)  # trocando o nome do usuário
                self.nickname = new_nickname
                print(msg)
                self.sendMsg(new_nickname,
                             Message(serverName, listClients[new_nickname][1].cliAddr, new_nickname, 'mostrar()', msg))

            # para este caso, o 'nickname' enviado é o do próprio usuário, visto que ele quer sair da conversa (privada/chat)
            elif cmd == 'sair()':
                if message.nickname in listPrivates:  # verifica se o chat é privado
                    msg = Message(serverName, listClients[listPrivates[message.nickname]][1].cliAddr,
                                  listPrivates[message.nickname], 'mostrar()',
                                  'usuário ' + message.nickname + ' cancelou o privado!')
                    # avisa para o colega que o chat privado foi desconectado, visto que o outro cancelou
                    self.sendMsg(message.nickname, msg)
                    listPrivates.pop(listPrivates[message.nickname])  # remove o amigo do privado
                    listPrivates.pop(message.nickname)  # remove o mesmo do privado
                else:
                    listClients[message.nickname][1].isLogged = False
                    self.sendMsgToAll(listClients[message.nickname][1].nickname + 'saiu!')
                    listClients[message.nickname][0].close()
                    break  # sai da Thread
            # 'message.nickname' representa para onde quero enviar 
            elif cmd == 'enviar()':
                #if message.nickname == listPrivates[self.nickname]:  # verifica se o chat é privado
                if message.nickname in listPrivates :
                    self.sendMsg(message.nickname,
                        Message(serverName, listClients[message.nickname][1].cliAddr, message.nickname, 'mostrar()', message.msg))
                elif message.nickname == 'All':
                    self.sendMsgToAll(message.msg)
                else :
                    self.sendMsg(self.nickname,
                        Message(serverName, listClients[self.nickname][1].cliAddr, self.nickname, 'mostrar()', 'solicite privado com ' + message.nickname))
            elif cmd == 'resposta()':
                # adicionando a relação entre os usuários
                if message.msg == 'Y' : 
                    listPrivates[self.nickname] = message.nickname
                    listPrivates[message.nickname] = self.nickname
                    self.sendMsg(self.nickname,
                        Message(serverName, listClients[self.nickname][1].cliAddr, self.nickname, 'mostrar()',
                                'você e ' + message.nickname + ' estão agora no privado'))
                    self.sendMsg(message.nickname,
                        Message(serverName, listClients[message.nickname][1].cliAddr, message.nickname,
                                'mostrar()', 'você e ' + self.nickname + ' estão agora no privado'))
                else :
                    self.sendMsg(self.nickname,
                        Message(serverName, listClients[self.nickname][1].cliAddr, self.nickname, 'mostrar()',
                            message.nickname + ' não aceitou a solicitação de privado'))

            else:
                self.sendMsg(self.nickname,
                             Message(serverName, listClients[self.nickname][1].cliAddr, self.nickname, 'mostrar()',
                                     'comando inválido!'))

print('The server has started... \n')
while 1:
    cliCon, cliAddr = serverSocket.accept()
    
    print('... usuário fazendo login ...')
    
    cliCon.sendto(pickle.dumps(Message(serverName, cliAddr, 'nickname', 'mostrar()',
    "\nInforme:\n\t* L: login\n\t* C: cadastro\n")), cliAddr)
    
    resp = Access(cliCon, cliAddr, pickle.loads(cliCon.recv(1024)).msg.upper())
    
    if resp.dados != None:
        Chat(cliCon, cliAddr, resp.dados[0]).start()