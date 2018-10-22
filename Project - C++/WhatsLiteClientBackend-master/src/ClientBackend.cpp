#include "ClientBackend.h"
using namespace std;

ClientBackend::ClientBackend() {}

ClientBackend::~ClientBackend()
{
    delete t_read;
}

bool ClientBackend::init_wsa()
{
    result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if(result != 0) {
        cout << "WSAStartup failed: " << result << endl;
        return false;
    }
    return true;
}

Message* ClientBackend::get_message()
{
    Message msg;
    msg_mutex.lock();
    msg = msg_queue.front();
    msg_queue.pop();
    msg_mutex.unlock();
    return new Message(msg);
}

bool ClientBackend::has_new_messages()
{
    msg_mutex.lock();
    bool result = msg_queue.size() > 0;
    msg_mutex.unlock();
    return result;
}

bool ClientBackend::connect_server(string ip, string porta)
{
    if(sock.connect(ip.c_str(), porta.c_str()) == SOCKET_OK)
    {
        connected = true;
        t_read = new thread(server_read, this);
        return true;
    }
    return false;
}

CMD_CODE ClientBackend::login(string username, string password)
{
    if (!connected || logged) return CMD_USER_INVALIDO;
    write_mutex.lock();
    if (!write_code(CMD_LOGAR_USER, &sock))
    {
        write_mutex.unlock();
        return CMD_DISCONNECTED;
    }
    if (!write_portion(username, &sock))
    {
        write_mutex.unlock();
        return CMD_DISCONNECTED;
    }
    if (!write_portion(password, &sock))
    {
        write_mutex.unlock();
        return CMD_DISCONNECTED;
    }
    write_mutex.unlock();
    CMD_CODE code = get_result();
    if(code == CMD_OK)
    {
        logged = true;
        logged_user = username;
    }
    return code;
}

CMD_CODE ClientBackend::new_user(string username, string password)
{
    if (!connected || logged) return CMD_USER_INVALIDO;
    write_mutex.lock();
    if (!write_code(CMD_NOVO_USER, &sock))
    {
        write_mutex.unlock();
        return CMD_DISCONNECTED;
    }
    if (!write_portion(username, &sock))
    {
        write_mutex.unlock();
        return CMD_DISCONNECTED;
    }
    if (!write_portion(password, &sock))
    {
        write_mutex.unlock();
        return CMD_DISCONNECTED;
    }
    write_mutex.unlock();
    CMD_CODE code = get_result();
    if(code == CMD_OK)
    {
        logged = true;
        logged_user = username;
    }
    return code;
}

CMD_CODE ClientBackend::get_result()
{
    while (current_code == 0)
    {
        std::this_thread::sleep_for (std::chrono::milliseconds(100));
    }
    cmd_mutex.lock();
    CMD_CODE code = current_code;
    current_code = (CMD_CODE)0;
    cmd_mutex.unlock();
    return code;
}

bool ClientBackend::is_logged()
{
    return logged;
}

bool ClientBackend::init()
{
    return init_wsa();
}

void ClientBackend::server_read()
{
    while(connected)
    {
        CMD_CODE code;
        if(!read_code(&sock, code))
        {
            connected = false;
            continue;
        }
        switch (code)
        {
        case CMD_MSG_ARMAZENADA:
        case CMD_MSG_ENTREGUE:
        case CMD_MSG_INVALIDA:
        case CMD_OK:
        case CMD_USER_INVALIDO:
        {
            cmd_mutex.lock();
            current_code = code;
            cmd_mutex.unlock();
            break;
        }
        case CMD_LOGOUT_USER:
        {
            logoff();
            continue;
            break;
        }
        case CMD_NOVA_MSG:
        {
            msg_mutex.lock();
            Message temp;
            if(!read_msg(&sock, temp)) disconnect();
            msg_queue.push(temp);
            msg_mutex.unlock();
            write_mutex.lock();
            if(!write_code(CMD_OK, &sock)) disconnect();
            write_mutex.unlock();
            break;
        }
        }
    }
}

CMD_CODE ClientBackend::logoff()
{
    logged = false;
    write_mutex.lock();
    if(!write_code(CMD_LOGOUT_USER, &sock))
    {
        write_mutex.unlock();
        logged_user = "";
        return CMD_DISCONNECTED;
    }
    if(!write_portion(logged_user, &sock))
    {
        write_mutex.unlock();
        logged_user = "";
        return CMD_DISCONNECTED;
    }
    write_mutex.unlock();
    logged_user = "";
    return get_result();
}

void ClientBackend::disconnect()
{
    logged = false;
    connected = false;
}

bool ClientBackend::is_connected() const { return connected; }

CMD_CODE ClientBackend::send_message(Message& msg)
{
    if (!connected || !logged) return CMD_DISCONNECTED;
    write_mutex.lock();
    send_msg(&sock, msg);
    write_mutex.unlock();
    return get_result();
}
