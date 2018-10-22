from socket import *

serverName = '10.0.0.14' #Meu IP atual, deve ser verificado sempre
serverPort = 12000

#cria o socket com IPv4 (AF_INET) usando TCP (SOCK_STREAM)
serverSocket = socket(AF_INET,SOCK_STREAM)

#permite que seja possivel reusar o endereco e porta do servidor caso seja encerrado incorretamente
serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)

#Vincula o socket com a porta
serverSocket.bind((serverName,serverPort))

serverSocket.listen(100)
print('The server has started... \n')


listClients = {}

"""Função para definir o nick name do cliente"""
def nick_name(cliCon)
    # requisita o nick_name do novo cliente
    cliCon.send(raw_input("Por favor, informe seu nickname: "))
    # nick_name digitado pelo cliente
    nick = cliCon.recv(1024).decode('utf-8')
    

def chat(cliCon,cliAddr):
    ''' verifica se o cliente já existe: 
        * caso exista: continua o programa
        * caso contrário: pergunta o nick_name para o usuário
    '''
    if(cliAddr not in listClients)
        listClients[cliAddr] = nick_name(cliCon)


    message = cliCon.recv(1024).decode('utf-8')
    print('Client escreveu: \n', message)

while 1:
    #Espera por novas conexões
    # cliCon é um novo socket criado para o cliente que acabou de se conectar
    # cliAddr é o endereço do cliente que acabou de se conectar
    cliCon, cliAddr = serverSocket.accept()

    # inicia um novo chat para o cliente
    threading.Thread(target=chat, args=(cliCon, cliAddr)).start()

    