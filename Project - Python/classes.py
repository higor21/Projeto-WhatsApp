#coding: utf-8

import sys, pickle

class cmd_:
    # comandos de clientes 
    LISTA = 0
    PRIVADO = 1
    SAIR = 2
    CG_NOME = 3 # trocar o nome
    RESPOSTA = 4
    ENVIAR = 5

    # comandos do servidor 
    MOSTRAR = 6 # apenas mostar mensagem na tela do cliente
    ACESSAR = 7 # pede 'nickname' e 'senha' do usuário 
    LOG_REG = 8 # solicita resposta de erro, após usuário errar a senha/nickname
    LOG_CAD = 9 # verifica se o cliente quer fazer o login ou o cadastro
    REQUISITO = 10 # requisita ao usuário sobre escolha: entrar ou não no privado
    ATUALIZAR = 11 # avisa o usuário para atualizar sua lista de usuários
    LISTA_USERS = 12 # informa ao cliente que está o enviando a lista de usuários 

    CMD_PADRAO = 13 # não faz nada

class User(object):
    def __init__(self, cliAddr, nickname, isLogged = True, listM = []):
        self.nickname = nickname
        self.isLogged = isLogged
        self.cliAddr = cliAddr
        self.listMessages = listM # lista de mensagens do cliente (caso ele acabe de entrar e já tenha mensagens para o mesmo)
    
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, value):
        self.__dict__ = value

    def __str__(self):
        return 'nickname: ' + self.nickname + ' - estado: ' + ('logado' if self.isLogged else 'deslogado')


class Message:
    def __init__(self, ip_src= '', ip_dest= '', nickname= '', command = -1, msg= '', bitstream = None):
        
        self.length   = len(msg)
        self.ip_src  = ip_src
        self.ip_dest  = ip_dest
        self.nickname = nickname + (6 - len(nickname))*' '
        self.command  = command
        self.msg     = msg

        if bitstream is not None:
            self.fromBitstream(bitstream)
            
    def buildBitstream(self):
        bitstream  = bytes(   [self.length]  )
        bitstream += bytes(   list( map(int, self.ip_src.split('.')) )   )
        bitstream += bytes(   list( map(int, self.ip_dest.split('.')) )   )
        bitstream += bytes(   self.nickname, 'utf-8')
        bitstream += bytes(   [self.command]  )
        bitstream += bytes(   self.msg, 'utf-8')
        return bitstream

    def __bytes__(self): # retorna a mensagem transformada em bytes
        return self.buildBitstream()

    def __len__(self): # retorna o tamanho da mensagem transformada em bytes
        return len(self.buildBitstream())

    def makeIP_fromBitstream(self,ip_bitstream):
        ip_bits = ip_bitstream

        ip_tmp = str( list( map(int, ip_bits) ) ) # saida do tipo: '[192, 168, 0, 1]'
        ip_tmp = ip_tmp.replace(' ','') #remove espacos
        ip_tmp = ip_tmp.replace(',','.')
        ip_tmp = ip_tmp.replace('[','')
        ip_tmp = ip_tmp.replace(']','')
        #ao final teremos algo do tipo: '192.168.0.1'
        return ip_tmp

    def fromBitstream(self, bitstream):
        self.length  = int( bitstream[0] )
        self.ip_src = self.makeIP_fromBitstream(bitstream[1:5])
        self.ip_dest = self.makeIP_fromBitstream(bitstream[5:9])
        self.nickname= bitstream[9:15].decode('utf-8')
        self.command = int(bitstream[15])
        self.msg    = bitstream[16:].decode('utf-8')

    def __str__(self):
        out = 'Tamanho da Menssagem:'  + str(self.length)  + '\n'
        out+= 'Origem(IP):\t' + str(self.ip_src) + '\n'
        out+= 'Destino(IP):\t' + str(self.ip_dest) + '\n'
        out+= 'Nickname:\t'+ str(self.nickname)+ '\n'
        out+= 'Comando:\t' + str(self.command) + '\n'
        out+= 'Mensagem:\t'    + str(self.msg)    + '\n'
        return out