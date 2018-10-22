from socket import *

serverName = '10.0.0.14' #Meu IP atual, deve ser verificado sempre
serverPort = 12000

#cria o socket com IPv4 (AF_INET) usando TCP (SOCK_STREAM)
serverSocket = socket(AF_INET,SOCK_STREAM)

#permite que seja possivel reusar o endereco e porta do servidor caso seja encerrado incorretamente
serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)

#Vincula o socket com a porta
serverSocket.bind((serverName,serverPort))

serverSocket.listen(1)
print('The server has started... \n')

def nick_name(cliCon)
    """Função para definir o nick name do cliente"""

    print("Por favor, informe seu nickname: ")
    nick = cliCon.recv(1024).decode('utf-8')
    return nick

def chat(cliCon,cliAddr):
    """Função para gerenciar o bate papo do cliente"""

    message = cliCon.recv(1024).decode('utf-8')
    print('Client escreveu: \n', message)

while 1:
    #Espera por novas conexões
    # cliCon é um novo socket criado para o cliente que acabou de se conectar
    # cliAddr é o endereço do cliente que acabou de se conectar
    cliCon, cliAddr = serverSocket.accept()

    tNickName = threading.Thread(target=nick_name, args=(cliCon))
    tNickName.start()
    print()