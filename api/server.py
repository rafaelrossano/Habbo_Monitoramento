import socket
import threading
import time
from db_functions import check_changes
from config.group_ids import *

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 8765
MAX_CLIENTS = 10

# Lista para armazenar clientes conectados
clients = []

# Função para enviar mensagem a todos os clientes conectados
def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            clients.remove(client)
            client.close()

# Função para enviar mensagens periodicamente
def periodic_broadcast():
    while True:
        time.sleep(10)  # Envia a cada 10 segundos (ajuste conforme necessário)
        message = input("> ")
        if message == '!DISCONNECT':
            break
        print("Enviando: ", message)
        broadcast(message)

# Função para lidar com clientes
def handle_client(client_socket):
    while True:
        try:
            # Recebe a mensagem do cliente (se necessário, mas não utilizado aqui)
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
        except:
            # Remove o cliente se houver um erro (por exemplo, desconexão)
            clients.remove(client_socket)
            client_socket.close()
            break

# Função principal do servidor
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)
    print(f"Servidor ouvindo em {HOST}:{PORT}")

    # Inicia a thread de broadcast periódico
    broadcast_thread = threading.Thread(target=changes_loop)
    broadcast_thread.daemon = True
    broadcast_thread.start()

    while True:
        client_socket, addr = server.accept()
        print(f"Nova conexão de {addr}")
        if len(clients) < MAX_CLIENTS:
            clients.append(client_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
        else:
            print("Máximo de clientes atingido. Conexão rejeitada.")
            client_socket.close()
            
            
def changes_loop():
    while True:
        if check_changes('oficiais'):
            broadcast('oficiais')
        if check_changes('oficiais_superiores'):
            broadcast('oficiais_superiores')
        if check_changes('corpo_executivo'):
            broadcast('corpo_executivo')
        if check_changes('corpo_executivo_superior'):
            broadcast('corpo_executivo_superior')
        if check_changes('pracas'):
            broadcast('pracas')
        if check_changes('acesso_a_base'):
            broadcast('acesso_a_base')
        
        time.sleep(10)

if __name__ == "__main__":
    #thread = threading.Thread(target=changes_loop, daemon=True)
    #thread.start()
    main()
