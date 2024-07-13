import sqlite3
import requests
from config.group_ids import *
from main import get_time
import time

def get_group_member_list(group_id: str):
    _url = f'https://www.habbo.com.br/api/public/groups/{group_id}/members'
    request = requests.get(_url)

    group_members_list = []

    for member in request.json():
        group_members_list.append(
            {'nickname': member['name'].strip(), 'mission': member['motto'], 'isAdmin': member['isAdmin']}
        )

    return group_members_list


def set_members_table(table_name):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        
        cursor.execute(f'''
        CREATE TABLE {table_name} (
        nickname TEXT NOT NULL,
        missao TEXT NOT NULL,
        isAdmin TEXT NOT NULL  
        )            
        ''')
        
        for member in get_group_member_list(ID_OFICIAIS):
            cursor.execute(f'''
            INSERT INTO {table_name} (nickname, missao, isAdmin) VALUES (?, ?, ?)
            ''', (member['nickname'], member['mission'], member['isAdmin']))
            
            conn.commit()
    finally:
        conn.close()
    


def read_table(table_name):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM {table_name}')
        
        table_output = cursor.fetchall()

        output_list = [{'nickname': profile[0], 'missao': profile[1], 'isAdmin': profile[2]} for profile in table_output]
        
        if len(output_list) == 0:
            return 'Empty table'
        return output_list
    finally:
        conn.close()

def commit_changes(group_name, nickname, status, date_time):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
        INSERT INTO {group_name} (nickname, status, date_time) VALUES (?, ?, ?)
        ''', (nickname, status, date_time))
        
        conn.commit()
    finally:
        conn.close() 
        
        
def overwrite_atts_table(table_name):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        
        cursor.execute(f'''
        CREATE TABLE {table_name} (
        nickname TEXT NOT NULL,
        status TEXT NOT NULL,
        date_time TEXT NOT NULL  
        )            
        ''')
        conn.commit()
    finally:
        conn.close()

def check_changes(group_name):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        table_output = []
        if len(table_output) == 0:
            return
        table_output = read_table(group_name)
        
        group_members_dict = []

        if group_name == 'oficiais':
            group_members_dict = get_group_member_list(ID_OFICIAIS)
        elif group_name == 'oficiais_superiores':
            group_members_dict == get_group_member_list(ID_OFICIAIS_SUPERIORES)
        elif group_name == 'corpo_executivo':
            group_members_dict == get_group_member_list(ID_CORPO_EXECUTIVO)
        elif group_name == 'corpo_executivo_superior':
            group_members_dict == get_group_member_list(ID_CORPO_EXECUTIVO_SUPERIOR)
        elif group_name == 'acesso_a_base':
            group_members_dict == get_group_member_list(ID_ACESSO_A_BASE)
        elif group_name == 'pracas':
            group_members_dict == get_group_member_list(ID_PRACAS)
            
        
        group_members = [member['nickname'] for member in group_members_dict]
        database_members = [member['nickname'] for member in table_output]

        
        for member in table_output:
            if member['nickname'] not in group_members:
                commit_changes(f'{group_name}_atts', member['nickname'], 'saiu', get_time('%d/%m/%Y - %H:%M:00'))
        
        for member in group_members_dict:
            if member['nickname'] not in database_members:
                commit_changes(f'{group_name}_atts', member['nickname'], 'entrou', get_time('%d/%m/%Y - %H:%M:00'))
                
        set_members_table(group_name)
    
        return
    
    finally:
        conn.close()


def remove_profile_from_db(profile_name, table_name):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
        DELETE from {table_name}
        WHERE nickname = ?              
        ''', (profile_name,))
        
        conn.commit()
        return
    finally:
        conn.close()


def list_tables():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_list = [table[0] for table in tables]
        return table_list
    finally:
        conn.close()
        
        
while True:
    time.sleep(5)
    check_changes('oficiais')
    print(read_table('oficiais'))
    print('----')
    print(read_table('oficiais_atts'))