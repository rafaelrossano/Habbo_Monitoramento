import socket
from db_functions import check_changes
import time

# Definir o endereço e a porta do servidor
HOST = '0.0.0.0'  # Aceitar conexões de qualquer endereço IP
PORT = 65432      # Porta a ser usada

# Criar o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print('Aguardando conexão do cliente...')

# Aguardar conexão do cliente
conn, addr = server_socket.accept()
print(f'Conectado por {addr}')

is_change = check_changes('riny')


def check_if_change_and_notify(group_name):
    if is_change:
        message = 'Houve uma mudança no grupo.'
        conn.sendall(message.encode())

try:
    while True:
       check_if_change_and_notify('riny')
       time.sleep(10)
finally:
    conn.close()
    server_socket.close()
