import socket


# Definir o endereço e a porta do servidor
HOST = '127.0.0.1'  # Substitua pelo endereço IP do servidor
PORT = 65432                   # Mesma porta que o servidor está usando

# Criar o socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    while True:
        # Receber a mensagem do servidor
        data = client_socket.recv(1024)
        if data:
            print(f'Mensagem do servidor: {data.decode()}')
finally:
    client_socket.close()
