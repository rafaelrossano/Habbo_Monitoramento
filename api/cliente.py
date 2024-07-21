import socket
import threading

# Configurações do cliente
HOST = '127.0.0.1'
PORT = 8765

# Função para receber mensagens do servidor
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except:
            print("Erro ao receber mensagem.")
            client_socket.close()
            break

# Função principal do cliente
def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print("Conectado ao servidor.")
    except:
        print("Erro ao conectar ao servidor.")
        return

    # Cria uma thread para receber mensagens do servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Mantém a conexão aberta
    while True:
        pass

