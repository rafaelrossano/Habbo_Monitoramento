import socket
import sqlite3
from shared_variables import groups_members, groups_members_lock, groups_atts, groups_atts_lock

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

def run_client(window): 
    # create a socket object 
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
 
    server_ip = "127.0.0.1"  # replace with the server's IP address 
    server_port = 8000  # replace with the server's port number 
    # establish connection with server 
    client.connect((server_ip, server_port)) 
 
    while True: 
        # receive message from the server 
        response = client.recv(1024) 
        response = response.decode("utf-8") # response será o grupo escrito em lower snake case. ex: "acesso_a_base"
        if len(response) > 0:
            with groups_members_lock:
                groups_members[response] = read_table(response)
            with groups_atts_lock:
                groups_atts[response] = read_table(response + "_atts")
            
            # IMPLEMENTAÇÃO DAS MUDANÇAS NOS GRUPOS
 
        # if server sent us "closed" in the payload, we break out of the loop and close our socket 
        if response.lower() == "closed": 
            break 
 
        print(f"Received: {response}") 
 
    # close client socket (connection to the server) 
    client.close() 
    print("Connection to server closed") 