#include "helpers.h"
bool operator==(User u1, User u2)
{
    return u1.username == u2.username;
}

bool read_code(tcp_winsocket* sock, CMD_CODE& code)
{
    char c;
    if (sock->read(&c, 1) <= 0)
    {
        return false;
    }
    code = (CMD_CODE)c;
    return true;
}

bool write_code(CMD_CODE code, tcp_winsocket* sock)
{
    std::string str;
    str += code;
    if(sock->write(str.c_str(), 1) <= 0)
    {
        return false;
    }
    return true;
}

bool read_portion(tcp_winsocket* sock, std::string& str)
{
    char c;
    if(sock->read(&c, 1) <= 0)
    {
        return false;
    }
    char buffer[c+1];
    if (sock->read(buffer, c) <= 0)
    {
        return false;
    }
    buffer[c] = 0;
    str = std::string(buffer);
    return true;
}

bool write_portion(std::string user, tcp_winsocket* socket)
{
    if (user.size() > 255)
    {
        std::cout << "Erro: std::string maior que o tamanho maximo" << std::endl;
        return true;
    }
    std::string buffer;
    buffer += user.size();
    buffer += user.c_str();
    if(socket->write(buffer.c_str(), buffer.size()) <= 0)
    {
        return false;
    }
    return true;
}

bool send_msg(tcp_winsocket* sock, const Message& msg)
{
    if (msg.content == "" || msg.receiver == "") return false;
    if(!write_code(CMD_NOVA_MSG, sock)) return false;
    if(!write_portion(msg.receiver, sock)) return false;
    if(!write_portion(msg.content, sock)) return false;
    return true;
}

bool read_msg(tcp_winsocket* sock, Message& msg)
{
    if (!read_portion(sock, msg.receiver)) return false;
    if (!read_portion(sock, msg.content)) return false;
    return true;
}
