#coding: utf-8

import sys, pickle


class Message:
    # construtor
    def __init__(self, ip_o = '', ip_d = '', nickname = '', command = '', msg = ''):
        self.ip_o, self.ip_d, self.msg  = ip_o, ip_d, msg
        self.nickname, self.command,= nickname, command
        self.size = sys.getsizeof(self) # tamanho da mensagem (incluindo a cabeçalho)

    def __str__(self):
        # definir melhor depois como será impressa a mensagem ...
        return 'orig: ' + self.ip_o + ', dest: ' + self.ip_d + ' -> message:\n\t' + self.msg

class User(object):
    def __init__(self, cliAddr, nickname, senha, disp = False, isLogged = True, listM = []):
        self.nickname = nickname
        self.disp, self.isLogged = disp, isLogged
        self.cliAddr = cliAddr
        self.listMessages = listM # lista de mensagens do cliente (caso ele acabe de entrar e já tenha mensagens para o mesmo)
        self.senha = senha 
    
    def __getstate__(self):
        print 'get'
        return self.__dict__

    def __setstate__(self, value):
        print 'set'
        self.__dict__ = value

    def __str__(self):
        strPriv = (' - lugar: privado' if self.disp else ' - lugar: chat público')
        return 'nickname: ' + self.nickname + ' - estado: ' + ('logado' if self.isLogged else 'deslogado')
