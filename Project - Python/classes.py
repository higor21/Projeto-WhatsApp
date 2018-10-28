#coding: utf-8

import sys, pickle


class Message:
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
