#ifndef CLIENTBACKEND_H
#define CLIENTBACKEND_H
#include "helpers.h"

class ClientBackend
{
    public:
        ClientBackend();
        ~ClientBackend();
        bool is_connected() const;
        bool has_new_messages();
        Message* get_message();
        bool connect_server(std::string ip, std::string porta);
        CMD_CODE login(std::string username, std::string password);
        CMD_CODE new_user(std::string username, std::string password);
        CMD_CODE send_message(Message& msg);
        void server_read();
        bool init();
        bool is_logged();
        void disconnect();
        CMD_CODE logoff();
    private:
        CMD_CODE get_result();
        WSADATA wsaData;
        WINSOCKET_STATUS result;
        tcp_winsocket sock;
        std::mutex cmd_mutex;
        std::mutex msg_mutex;
        std::mutex write_mutex;
        std::string logged_user;
        bool connected = false;
        bool logged = false;
        CMD_CODE current_code = (CMD_CODE)0;
        std::queue<Message> msg_queue;
        std::thread* t_read;
        bool init_wsa();
        void write_user_and_pass(std::string& user, std::string& pass, tcp_winsocket sock);
};

#endif // CLIENTBACKEND_H
