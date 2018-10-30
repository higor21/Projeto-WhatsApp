#coding: utf-8

import sys, pickle


class Message_:
    # construtor
    def __init__(self, ip_src = '', ip_dest = '', nickname = '', command = '', msg = ''):
        self.ip_src, self.ip_dest, self.msg  = ip_src, ip_dest, msg
        self.nickname, self.command = nickname, command
        self.size = sys.getsizeof(self) # tamanho da mensagem (incluindo a cabeçalho)

    def __str__(self):
        # definir melhor depois como será impressa a mensagem ...
        return 'message:  ' + self.msg
    

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
        self.nickName = nickname
        self.command  = command
        self.msg     = msg

        if bitstream is not None:
            self.fromBitstream(bitstream)
            
    def buildBitstream(self):
        bitstream  = bytes(   [self.length]  )
        bitstream += bytes(   list( map(int, self.ip_src.split('.')) )   )
        bitstream += bytes(   list( map(int, self.ip_dest.split('.')) )   )
        bitstream += bytes(self.nickName,  'utf-8')
        bitstream += bytes(   [self.command]  )
        bitstream += bytes(self.msg, 'utf-8')
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
        self.length  = int(bitstream[0])
        self.ip_src = self.makeIP_fromBitstream(bitstream[1:5])
        self.ip_dest = self.makeIP_fromBitstream(bitstream[5:9])
        self.nickName= bitstream[9:15].decode('utf-8')
        self.command = int(bitstream[15])
        self.msg    = bitstream[16:].decode('utf-8')

    def __str__(self):
        out = 'Tamanho da Menssagem:'  + str(self.length)  + '\n'
        out+= 'Origem(IP):\t' + str(self.ip_src) + '\n'
        out+= 'Destino(IP):\t' + str(self.ip_dest) + '\n'
        out+= 'Nickname:\t'+ str(self.nickName)+ '\n'
        out+= 'Comando:\t' + str(self.command) + '\n'
        out+= 'Mensagem:\t'    + str(self.msg)    + '\n'
        return out