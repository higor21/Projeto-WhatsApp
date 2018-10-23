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
    * enviar(): apenas envia a mensagem. O destino para o qual será enviada depende da variável 'mode' do chat 
'''
from socket import *
from threading import Thread

serverName = '192.168.0.9' #Meu IP atual, deve ser verificado sempre
serverPort = 12000

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
serverSocket.bind((serverName,serverPort))

serverSocket.listen(100)
print('The server has started... \n')

# lista de usuário 
listClients = {}


class Message:
    # construtor
    def __init__(self, ip_o = '', ip_d = '', nickname = '', command = '', msg = ''):
        self.ip_o, self.ip_d, self.msg  = ip_o, ip_d, msg
        self.nickname, self.command,= nickname, command
        self.size = sys.getsizeof(self) # tamanho da mensagem (incluindo a cabeçalho)

    def __str__(self):
        # definir melhor depois como será impressa a mensagem ...
        return 'orig: ' + self.ip_o + ', dest: ' + self.ip_d + ' -> message:\n\t' + self.msg

class User:
    # construtor
    def __init__(self, cliCon, nickname, disp = False, isLogged = True, listM = []):
        self.cliCon, self.nickname = cliCon, nickname
        self.disp, self.isLogged = disp, isLogged
        self.listMessages = listM # lista de mensagens do cliente (caso ele acabe de entrar e já tenha mensagens para o mesmo)
    
    def __str__(self)
        return 'nickname: ' + self.nickname + ' - estado: ' + \
        (('logado' + (' - lugar: privado' if self.disp else ' - lugar: chat público')) if self.isLogged else 'deslogado')
        

class Chat(Thread):
    # construtor
    def __init__(self, cliCon, cliAddr, mode = False):
        Thread.__init__(self)
        self.cliCon = cliCon
        self.cliAddr = cliAddr 

        self.mode = mode # define se o chat atual é público ou privado
        self.friend = None # usuário que representa o colega do chat privado
        
        if(cliAddr not in listClients):
            cliCon.sendto("Por favor, informe seu nickname: ", cliAddr)
            nick = cliCon.recv(1024).decode('utf-8')
            # 'False' indica que o usuário não está no privado com ninguém 
            # 'True' indica que o usuário está logado
            listClients[cliAddr] = User(cliCon, nick)
            print listClients[cliAddr]
        else: 
            listClients[cliAddr].isLogged = True
            listClients[cliAddr].cliCon = cliCon
            if listClients[cliAddr].listMessages : # caso tenha mensagens nova para o usuário, envia as mensagens para o mesmo
                self.sendMsg(listClients[cliAddr], listClients[cliAddr].listMessages)
        self.sendMsg(listClients[cliAddr].nickname + ' entrou...') # LEMBRAR DE FORMULAR MENSAGEM AQUI (usar construtor de 'Mensagem')
        Thread(target=self.receiveData).start() # espera por mensagem do usuário 

    def sendMsg(self, user, msg):
        if type(msg) is not list: # verifica se há uma lista de mensagens
            msg = [msg]
        if user.isLogged: 
            map(lambda x: self.cliCon.sendto(x, user.cliAddr), msg) # TESTAR SE ISSO FUNCIONA (acho que é necessário um 'for')
        else 
            user.listMessages += msg
    
    def sendMsgToAll(self, msg):
        for C in listClients:
            self.sendMsg(C,msg)
        
    def receiveData(self):
        while(True):
            message = self.cliCon.recv(1024).decode('utf-8')
            cmd = message.command
            print('Client escreveu: \n', message)

            if cmd == 'lista()':
                self.cliCon.sendto(listClients,self.cliAddr)
            elif cmd.startswith('privado(') and cmd.endswith(')'): # verifica se o comando é privado(*) M
                # verifica se o 'nickname' existe 
                if message.nickname[len('privado('):len(message.nickname)-1] == listClients[message.ip_d] :
                    if not listClients[message.ip_d].isLogged :
                        pass # retornar mensagem dizendo que o usuário não está disponível
                    elif listClients[message.ip_d].disp : 
                        pass # retornar mensagem informando que o usuário já está no privado
                    else
                        pass # enviar mensagem 
                    
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
    cliCon, cliAddr = serverSocket.accept()
    # False: chat público (padrão)
    # True: chat privado 
    Chat(cliCon, cliAddr).start()
