import socket
import sqlite3
from shared_variables import groups_members, groups_members_lock, groups_atts, groups_atts_lock
import threading

def read_table(table_name):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM {table_name}')
        
        table_output = cursor.fetchall()

        output_list = [{'nickname': profile[0], 'missao': profile[1], 'isAdmin': profile[2]} for profile in table_output]
        
        if len(output_list) == 0:
            return []
        return output_list
    finally:
        conn.close()

def commit_changes(table_name, nickname, status, date_time):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
                INSERT INTO {table_name} (nickname, status, date_time) VALUES (?, ?, ?)
                ''', (nickname, status, date_time))
        
        # Salvar (commit) as mudanças
        conn.commit()
    finally:
        conn.close() 

# Configurações do cliente
HOST = '127.0.0.1'
PORT = 8765

# Função principal do cliente
def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print("Conectado ao servidor.")
        
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
        
    except:
        print("Erro ao conectar ao servidor.")
        return

    # Cria uma thread para receber mensagens do servidor
    receive_thread = threading.Thread(target=run_client)
    receive_thread.start()

    # Mantém a conexão aberta
    while True:
        pass
    
run_client()