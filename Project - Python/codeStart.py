#coding: utf-8
'''################################## DÚVIDAS
    * Os dados de cada cliente deve permanecer na lista caso ele dislogue?
    * Explicação relacionada aos 'bytes' da mensagem 
    * Todos os 'nicknames' devem ser distintos?
'''##################################
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

''' FALTA FAZER O USUÁRIO '''
class User:
    # construtor
    def __init__(self, cliCon, nickname, disp = False, isLogged = True):
        pass

class Chat(Thread):
    # construtor
    def __init__(self, cliCon, cliAddr, listM = ()):
        Thread.__init__(self)
        self.cliCon = cliCon
        self.cliAddr = cliAddr
        self.listMessages = listM # lista de mensagens do cliente (caso ele acabe de entrar e já tenha mensagens para o mesmo)
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
        self.sendData(listClients[cliAddr].nickname + ' entrou...')
        Thread(target=self.receiveData).start() # espera por mensagem do usuário 

    def sendData(self, msg = ''): # 'msg' representa a mensagem 'nick-name entrou...'
        if msg != '':
            pass # AINDA FALTA FAZER 
        
    def receiveData(self):
        while(True):
            message = self.cliCon.recv(1024).decode('utf-8')
            cmd = message.command
            print('Client escreveu: \n', message)

            if cmd == 'lista()':
                self.cliCon.sendto(listClients,self.cliAddr)
            elif cmd.startswith('privado(') and cmd.endswith(')'): # verifica se o comando é privado(*)
                # verifica se o 'nickname' existe 
                if message.nickname[len('privado('):len(message.nickname)-1] == listClients[message.ip_d] :
                    '''
                        CRIAR UM CLAT PRIVADO (OU FAZER ESSE SITE TER DOIS MODOS, PRIVADO E PÚBLICO) E CHAMAR UMA THREAD AQUI
                    '''
            elif cmd.startswith('nome(') and cmd.endswith(')'): # verifica se o comando é nome(*)
                new_nickname = message.nickname[len('nome('):len(message.nickname)-1]
                self.sendData(listClients[message.ip_o].nickname + ' agora é ' + new_nickname)
                listClients[message.ip_o].nickname = message.nickname[len('nome('):len(message.nickname)-1]
                
            elif cmd == 'sair()': 
                listClients[message.ip_o].isLogged = False
                self.sendData(listClients[message.ip_o].nickname + 'saiu!')
                self.cliCon.close()
                break
            else:
                self.sendData('comando inválido!\n')

while 1:
    cliCon, cliAddr = serverSocket.accept()
    print "dafdf"
    Chat(cliCon, cliAddr).start()

    