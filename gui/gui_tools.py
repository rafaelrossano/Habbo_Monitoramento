import socket
import sqlite3
import threading
import requests


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

def get_group_members(group_id: str):
    _url = f'https://www.habbo.com.br/api/public/groups/{group_id}/members'
    request = requests.get(_url)

    group_members_list = []

    for member in request.json():
        group_members_list.append(
            {'nickname': member['name'].strip(), 'mission': member['motto'], 'isAdmin': member['isAdmin']}
        )

    return group_members_list

def get_group_atts(group: str):
    _url = f'http://54.84.253.156/atts/{group}'
    request = requests.get(_url)

    group_atts_list = []

    for att in request.json():
        group_atts_list.append(
            {'nickname': att['nickname'].strip(), 'type': att['type'], 'date_time': att['date_time']}
        )

    return group_atts_list

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

HOST = '127.0.0.1'
PORT = 8765

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print("Conectado ao servidor.")
    except Exception as e:
        print(e)
        return

    # Cria uma thread para receber mensagens do servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Mantém a conexão aberta
    while True:
        pass