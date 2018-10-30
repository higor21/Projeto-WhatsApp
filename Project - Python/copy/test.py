#coding: utf-8
import pickle, sys

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
    def __init__(self, cliCon, cliAddr, nickname, disp = False, isLogged = True, listM = []):
        self.cliCon, self.nickname = cliCon, nickname
        self.disp, self.isLogged = disp, isLogged
        self.cliAddr = cliAddr
        self.listMessages = listM # lista de mensagens do cliente (caso ele acabe de entrar e já tenha mensagens para o mesmo)
    
    def __getstate__(self):
        print('dfjasldjfçlas')
        return self.__dict__

    def __setstate__(self, value):
        self.__dict__ = value

    def __str__(self):
        strPriv = (' - lugar: privado' if self.disp else ' - lugar: chat público')
        return 'nickname: ' + self.nickname + ' - estado: ' + ('logado' if self.isLogged else 'deslogado')

f = User(4,5,'higor')
f_string = pickle.dumps(f)
f_new = pickle.loads(f_string)
print f_new