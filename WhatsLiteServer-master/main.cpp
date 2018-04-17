#include "helpers.h"
#include "conf.h"
#include <fstream>
#include <sstream>
#include <winsock2.h>
#include <ws2tcpip.h>

HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);

using namespace std;
User* user_find_by_socket(tcp_winsocket*);
User* user_find(string);
void error_invalid_user(tcp_winsocket*);
/// Variaveis globais
WSADATA wsaData;
tcp_winsocket_server socket_server;
std::mutex write_mutex;

list<User> users;

list<tcp_winsocket*> logged_users;

queue<Message> to_send;
queue<string> to_send_dest;

list<tcp_winsocket*> to_remove;

list<tcp_winsocket*> clients_sockets;
bool ended = false; // define se o servidor encerrou ou nao

void remove_all(list<tcp_winsocket*>& lista, list<tcp_winsocket*>& from)
{
    for (tcp_winsocket* sock : lista)
    {
        User* temp = user_find_by_socket(sock);
        if (temp != NULL)
        {
            temp->sock = NULL;
        }
        from.remove(sock);
        logged_users.remove(sock);
        delete sock;
    }
    lista.clear();
}

void init_server()
{
    if(WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        cout << "WSAStartup failed" << endl;
        exit(1);
    }

    if (socket_server.listen(SERVER_PORT, NUM_MAX_CONEX) != SOCKET_OK) {
        cerr << "Não foi possível abrir o socket de controle\n";
        exit(1);
    }

    cout << "Server Iniciado na porta 23456" << endl;
}

bool is_logged(tcp_winsocket* sock)
{
    return find(logged_users.begin(), logged_users.end(), sock) != logged_users.end();
}

bool is_logged(string username)
{
    User* user = user_find(username);
    return is_logged(user->sock);
}

bool user_exists(string username)
{
    User* temp = user_find(username);
    return temp != NULL;
}

User* user_find(string username)
{
    User temp = { username };
    auto result = find(users.begin(), users.end(), temp);
    return (result == users.end()) ? NULL : &(*result);
}

User* user_find_by_socket(tcp_winsocket* sock)
{
    auto temp = find_if(users.begin(), users.end(), [sock](User& u) -> bool { return u.sock == sock; });
    return (temp == users.end()) ? NULL : &(*temp);
}

void user_set_socket(tcp_winsocket* sock, string username)
{
    User* temp = user_find(username);
    if (temp != NULL) temp->sock = sock;
}

void write_error_and_remove(tcp_winsocket* sock)
{
    //cout << "Erro ao ler o codigo do comando no socket. Fechando conexao..." << endl;
    to_remove.push_back(sock);
}

void error_invalid_user(tcp_winsocket* sock)
{
    write_mutex.lock();
    if(!write_code(CMD_USER_INVALIDO, sock))
    {
       write_error_and_remove(sock);
    }
    write_mutex.unlock();
}

void error_invalid_message(tcp_winsocket* sock)
{
    write_mutex.lock();
    if(!write_code(CMD_MSG_INVALIDA, sock))
    {
       write_error_and_remove(sock);
    }
    write_mutex.unlock();
}

void handle_clients(winsocket_queue& socket_queue)
{
    for(tcp_winsocket* sock : clients_sockets)
    {
        if (socket_queue.had_activity(*sock))
        {
            CMD_CODE code;
            if(!read_code(sock, code))
            {
                write_error_and_remove(sock);
                continue;
            }

            if (code == CMD_LOGAR_USER)
            {
                if (is_logged(sock)) { error_invalid_user(sock); continue; }

                string username;
                if(!read_portion(sock, username)) { write_error_and_remove(sock); continue; }

                User* usuario = user_find(username);
                if (usuario == NULL) { error_invalid_user(sock); continue; }

                if (usuario->sock != NULL) { error_invalid_user(sock); continue; }

                string pass;
                if (!read_portion(sock, pass)) { write_error_and_remove(sock); continue; }

                if (pass != usuario->pass) { error_invalid_user(sock); continue; }

                if (!write_code(CMD_OK, sock)) { write_error_and_remove(sock); continue; }

                if (usuario->msg_list.size() > 0)
                {
                    while (usuario->msg_list.size() > 0)
                    {
                        to_send.push(usuario->msg_list.front());
                        to_send_dest.push(usuario->username);
                        usuario->msg_list.pop_front();
                    }
                }
                logged_users.push_back(sock);
                user_set_socket(sock, username);
            }
            else if (code == CMD_NOVO_USER)
            {
                if (is_logged(sock)) { error_invalid_user(sock); continue; }

                string username;
                if(!read_portion(sock, username))  { write_error_and_remove(sock); continue; }

                if (user_exists(username) || username == "") { error_invalid_user(sock); continue; }

                string pass;
                if (!read_portion(sock, pass)) { write_error_and_remove(sock); continue;}

                if (pass == "") { error_invalid_user(sock); continue; }

                if (!write_code(CMD_OK, sock)) {  write_error_and_remove(sock); continue; }

                users.push_back(User {username, pass, list<Message>(), NULL});
                logged_users.push_back(sock);
                user_set_socket(sock, username);
            }
            else if(code == CMD_NOVA_MSG)
            {
                Message temp;
                bool result = read_msg(sock, temp);
                if (!result) {
                    error_invalid_message(sock);
                    continue;
                }

                User* from = user_find_by_socket(sock);
                User* dest = user_find(temp.receiver);
                temp.receiver = from->username;

                if(dest == NULL || from == NULL || dest == from) { error_invalid_user(sock); continue; }

                if(is_logged(dest->sock))
                {
                    write_mutex.lock();
                    if (!send_msg(dest->sock, temp))
                    {
                        write_error_and_remove(sock);
                        dest->msg_list.push_back(temp);
                        if(!write_code(CMD_MSG_ARMAZENADA, sock))
                        {
                            write_error_and_remove(sock);
                            write_mutex.unlock();
                            continue;
                        }
                    }
                    else
                    {
                        if(!write_code(CMD_MSG_ENTREGUE, sock))
                        {
                            write_error_and_remove(sock);
                            write_mutex.unlock();
                            continue;
                        }
                    }
                    write_mutex.unlock();
                }
                else
                {
                    dest->msg_list.push_back(temp);
                    write_mutex.lock();
                    if(!write_code(CMD_MSG_ARMAZENADA, sock))
                    {
                        write_error_and_remove(sock);
                        write_mutex.unlock();
                        continue;
                    }
                    write_mutex.unlock();
                }
            }
            else if(code == CMD_LOGOUT_USER)
            {
                string username;
                if(!read_portion(sock, username)) { write_error_and_remove(sock); continue; }

                User* us = user_find(username);
                if (us == NULL)  { error_invalid_user(sock);  continue; }

                if(us->sock != sock) {  error_invalid_user(sock);  continue; }

                logged_users.remove(us->sock);
                us->sock = NULL;

                write_mutex.lock();
                if (!write_code(CMD_OK, sock)) write_error_and_remove(sock);
                write_mutex.unlock();
            }
        }
    }
    remove_all(to_remove, clients_sockets);
}

void handle_connections(winsocket_queue& socket_queue)
{
    tcp_winsocket socket;
    if (socket_queue.had_activity(socket_server))
    {
        if (socket_server.accept(socket) == SOCKET_OK)
        {
            cout << "Novo cliente conectado" << endl << "> ";
            clients_sockets.push_back(new tcp_winsocket(socket));
        }
        else
        {
            cerr << "Nao foi possivel estabelecer conexao";
            ended = true;
        }
    }
}

void server_write()
{
    while(!ended)
    {
        std::this_thread::sleep_for (std::chrono::milliseconds(100));
        if (to_send.size() > 0)
        {
            while(to_send.size() > 0)
            {
                write_mutex.lock();
                Message msg = to_send.front();
                string dest = to_send_dest.front();
                to_send.pop();
                to_send_dest.pop();
                tcp_winsocket* sock = user_find(dest)->sock;
                if(!send_msg(sock, msg))
                {
                    write_error_and_remove(sock);
                }
                write_mutex.unlock();
            }
        }
    }
}

void server_read()
{
    winsocket_queue socket_queue;
    int result;

    while(!ended)
    {
        socket_queue.clean();

        if(socket_server.accepting())
        {
            socket_queue.include(socket_server);

            for(tcp_winsocket* so : clients_sockets)
            {
                socket_queue.include(*so);
            }
        }
        else
        {
            ended = true;
            break;
        }
        result = socket_queue.wait_read();
        if(result == SOCKET_ERROR)
        {
            cerr << endl << "Erro na espera por atividades" << endl;
        }
        else if (result != 0)
        {
            handle_clients(socket_queue);
            handle_connections(socket_queue);
        }
    }
}



int main()
{
    init_server();
    thread t_write(server_write);
    thread t_read(server_read);
    t_write.join();
    t_read.join();
    return 0;
}
