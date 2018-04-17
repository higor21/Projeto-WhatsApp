#ifndef USUARIO_H
#define USUARIO_H

#include <iostream>
#include <vector>
#include <list>
#include "winsocket.h"
#include <map>
#include <thread>
#include <algorithm>
#include <queue>
#include <chrono>
#include <mutex>

enum CMD_CODE
{
    // Comandos do servidor
    CMD_DISCONNECTED = 0,
    CMD_OK = 1,
    CMD_USER_INVALIDO = 3,
    CMD_MSG_INVALIDA = 6,
    CMD_MSG_ENTREGUE = 7,
    CMD_MSG_ARMAZENADA = 8,
    // Comandos do cliente
    CMD_NOVO_USER = 2,
    CMD_LOGAR_USER = 4,
    // Comandos do cliente e servidor
    CMD_NOVA_MSG = 5,
    CMD_LOGOUT_USER = 9
};
struct Message
{
    std::string receiver;
    std::string content;
};

// Struct para armazenar os dados dos usuário cadastrados no servidor.
struct User
{
    std::string username;
    std::string pass;
    std::queue<Message> msg_queue;
    tcp_winsocket* sock;
};
bool operator==(User u1, User u2);
bool read_code(tcp_winsocket* sock, CMD_CODE& code);
bool write_code(CMD_CODE code, tcp_winsocket* sock);
bool read_portion(tcp_winsocket* sock, std::string& str);
bool write_portion(std::string user, tcp_winsocket* socket);
bool send_msg(tcp_winsocket* sock, const Message& msg);
bool read_msg(tcp_winsocket* sock, Message& msg);

#endif // USUARIO_H
