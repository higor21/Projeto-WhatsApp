#include "ClientBackend.h"
#include <windows.h>

using namespace std;

ClientBackend client_back;



void imprimir_msgs()
{
    while(client_back.is_connected())
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        cout << "dentro" << endl;
        if (client_back.has_new_messages())
        {
            Message* msg = client_back.get_message();
            cout << "Mensagem de " << msg->receiver << ": " << msg->content << endl << endl;
        }
    }
}

void imprimir_opcoes()
{
    cout << "Opcoes: " << endl;
    cout << "- Deslogar: d"<< endl << "- Novo usuario: nu usuario senha " <<
    endl << "- Logar Usuario: lu usuario senha" << endl << "- Ler novas mensagens: lm" <<
    endl << "- Enviar mensagem: em usuario mensagem" << endl << "- Ajuda comandos: h" << endl <<
     "- Limpar tela: cls" << endl << endl;
}

int main()
{
    string title = "Deslogado";
    SetConsoleTitle(title.c_str());
    string code = "";
    string user, pass;
    ClientBackend client_back;
    if (!client_back.init())
    {
        cout << "Nao foi possivel iniciar o WinSock..." << endl;
        return 1;
    }
    string server;
    string porta;
    cout << "Digite o servidor e porta: ";
    cin >> server;
    cin >> porta;
    if (!client_back.connect_server(server, porta))
    {
        cout << "Nao foi possível conectar ao servidor..." << endl;

        return 1;
    }
    cout << "Conectado ao servidor "<< server << endl;
    imprimir_opcoes();
    std::thread t_write_msgs(imprimir_msgs);
    while (client_back.is_connected())
    {
        cout << "> ";
        cin >> code;
        if (code == "nu")
        {
            cin >> user;
            cin >> pass;
            if (client_back.is_logged())
            {
                cout << "Voce ja esta logado" << endl;
                continue;
            }
            CMD_CODE code = client_back.new_user(user, pass);
            switch (code)
            {
            case CMD_DISCONNECTED:
                cout << "Usuario desconectado" << endl;
                return 0;
                break;
            case CMD_USER_INVALIDO:
                cout << "Usuario ou senha invalidos" << endl << endl;
                break;
            case CMD_OK:
                cout << "Usuario cadastrado e logado" << endl << endl;
                string title = "Logado como: ";
                title += user;
                SetConsoleTitle(title.c_str());
                break;
            }
        } else if (code == "lu")
        {

            cin >> user;
            cin >> pass;
            if (client_back.is_logged())
            {
                cout << "Voce ja esta logado" << endl;
                continue;
            }
            CMD_CODE code = client_back.login(user, pass);
            switch (code)
            {
            case CMD_DISCONNECTED:
                cout << "Usuario desconectado" << endl << endl;

                return 0;
                break;
            case CMD_USER_INVALIDO:
                cout << "Usuario ou senha invalidos" << endl << endl;
                break;
            case CMD_OK:
                cout << "Usuario logado" << endl << endl;
                string title = "Logado como: ";
                title += user;
                SetConsoleTitle(title.c_str());
                break;
            }
        } else if (code == "lm")
        {
            if (!client_back.is_logged())
            {
                cout << "Voce nao esta logado" << endl;
                continue;
            }
            if (!client_back.has_new_messages())
            {
                cout << "Vc nao tem novas mensagens" << endl << endl;
                continue;
            }
            while(client_back.has_new_messages())
            {
                Message* msg = client_back.get_message();
                cout << "Mensagem de " << msg->receiver << ": " << msg->content << endl << endl;
            }
        } else if (code == "em")
        {
            if (!client_back.is_logged())
            {
                cout << "Voce nao esta logado" << endl;
                continue;
            }
            Message temp;
            cin >> temp.receiver;
            cin.ignore(1, '\n');
            getline(cin, temp.content);
            CMD_CODE result = client_back.send_message(temp);
            switch(result)
            {
            case CMD_USER_INVALIDO:
                cout << "Usuario nao existe" << endl << endl;
                break;
                continue;
            case CMD_MSG_INVALIDA:
                cout << "Mensagem invalida" << endl << endl;
                break;
            case CMD_MSG_ARMAZENADA:
            case CMD_MSG_ENTREGUE:
                cout << "Mensagem enviada" << endl << endl;
                break;
            case CMD_DISCONNECTED:
                cout << "Usuario desconectado..." << endl << endl;

                return 1;
            }
        } else if (code == "h") imprimir_opcoes();
        else if (code == "d")
        {
            if (!client_back.is_logged())
            {
                cout << "Voce nao esta logado" << endl;
                continue;
            }
            while(client_back.has_new_messages())
            {
                Message* msg = client_back.get_message();
                cout << "Mensagem de " << msg->receiver << ": " << msg->content << endl << endl;
            }
            CMD_CODE result = client_back.logoff();
            if (result == CMD_DISCONNECTED)
            {
                cout << "O usuario foi desconectado do servidor..." << endl;

                return 1;
            } else if(result == CMD_USER_INVALIDO)
            {
                cout << "Voce nao pode deslogar outro usuario!" << endl;
                continue;
            }
            cout << "Voce deslogou" << endl << endl;
            SetConsoleTitle("Deslogado");
        }
        else if(code == "cls")
        {
            system("cls");
        }
        else
        {
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
    }
    return 0;
}
