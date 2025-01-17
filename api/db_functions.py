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
        
        if table_name == 'oficiais':
            for member in get_group_member_list(ID_OFICIAIS):
                cursor.execute(f'''
                INSERT INTO {table_name} (nickname, missao, isAdmin) VALUES (?, ?, ?)
                ''', (member['nickname'], member['mission'], member['isAdmin']))
            
            conn.commit()
            
        elif table_name == 'oficiais_superiores':
            for member in get_group_member_list(ID_OFICIAIS_SUPERIORES):
                cursor.execute(f'''
                INSERT INTO {table_name} (nickname, missao, isAdmin) VALUES (?, ?, ?)
                ''', (member['nickname'], member['mission'], member['isAdmin']))
                
            conn.commit()
            
        elif table_name == 'corpo_executivo':
            for member in get_group_member_list(ID_CORPO_EXECUTIVO):
                cursor.execute(f'''
                INSERT INTO {table_name} (nickname, missao, isAdmin) VALUES (?, ?, ?)
                ''', (member['nickname'], member['mission'], member['isAdmin']))
                
            conn.commit()
            
        elif table_name == 'corpo_executivo_superior':
            for member in get_group_member_list(ID_CORPO_EXECUTIVO_SUPERIOR):
                cursor.execute(f'''
                INSERT INTO {table_name} (nickname, missao, isAdmin) VALUES (?, ?, ?)
                ''', (member['nickname'], member['mission'], member['isAdmin']))
                
            conn.commit()
            
        elif table_name == 'acesso_a_base':
            for member in get_group_member_list(ID_ACESSO_A_BASE):
                cursor.execute(f'''
                INSERT INTO {table_name} (nickname, missao, isAdmin) VALUES (?, ?, ?)
                ''', (member['nickname'], member['mission'], member['isAdmin']))
                
            conn.commit()
            
        elif table_name == 'pracas':
            for member in get_group_member_list(ID_PRACAS):
                cursor.execute(f'''
                INSERT INTO {table_name} (nickname, missao, isAdmin) VALUES (?, ?, ?)
                ''', (member['nickname'], member['mission'], member['isAdmin']))
                
            conn.commit()
            
        elif table_name == 'riny':
            for member in get_group_member_list(ID_RINY):
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
        cursor.execute(f'SELECT * FROM "{table_name}"')
        
        table_output = cursor.fetchall()

        output_list = [{'nickname': profile[0], 'missao': profile[1], 'isAdmin': profile[2]} for profile in table_output]
        
        if len(output_list) == 0:
            return []
        return output_list
    finally:
        conn.close()
        

def read_atts_table(table_name):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM "{table_name}"')
        
        table_output = cursor.fetchall()

        output_list = [{'nickname': profile[0], 'status': profile[1], 'date_time': profile[2]} for profile in table_output]
        
        if len(output_list) == 0:
            return []
        return output_list
    finally:
        conn.close()


def insert_manually_to_atts_table(table_name, nickname, status, date_time):
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
        
        
        
def clear_atts_table(table_name):
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
    # Abrir a conexão no início da função
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    
    changes = False
    
    try:
        # Ler a tabela do banco de dados
        table_output = read_table(group_name)
        
        
        if len(table_output) == 0:
            return

        # Inicializar a lista de membros do grupo
        group_members_dict = []

        # Determinar o ID do grupo com base no nome do grupo
        if group_name == 'oficiais':
            group_members_dict = get_group_member_list(ID_OFICIAIS)
        elif group_name == 'oficiais_superiores':
            group_members_dict = get_group_member_list(ID_OFICIAIS_SUPERIORES)
        elif group_name == 'corpo_executivo':
            group_members_dict = get_group_member_list(ID_CORPO_EXECUTIVO)
        elif group_name == 'corpo_executivo_superior':
            group_members_dict = get_group_member_list(ID_CORPO_EXECUTIVO_SUPERIOR)
        elif group_name == 'acesso_a_base':
            group_members_dict = get_group_member_list(ID_ACESSO_A_BASE)
        elif group_name == 'pracas':
            group_members_dict = get_group_member_list(ID_PRACAS)
        elif group_name == 'riny':
            group_members_dict = get_group_member_list(ID_RINY)

        # Extrair os nomes dos membros dos dicionários
        group_members = [member['nickname'] for member in group_members_dict]
        database_members = [member['nickname'] for member in table_output]

        # Verificar membros que saíram
        for member in table_output:
            if member['nickname'] not in group_members:
                insert_manually_to_atts_table(f'{group_name}_atts', member['nickname'], 'saiu', get_time('%d/%m/%Y - %H:%M:00'))
                changes = True

        # Verificar membros que entraram
        for member in group_members_dict:
            if member['nickname'] not in database_members:
                insert_manually_to_atts_table(f'{group_name}_atts', member['nickname'], 'entrou', get_time('%d/%m/%Y - %H:%M:00'))
                changes = True

        # Atualizar a tabela de membros
        set_members_table(group_name)

        # Fechar a conexão
        conn.close()

        return changes
    
    except Exception as e:
        # Fechar a conexão em caso de exceção
        conn.close()
        raise e
    


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



def check_if_change(group_name):
    while True:
        print('procurando...')
        if check_changes(group_name):
            print('Entrou ou saiu')
            
            
def set_all_tables():

    set_members_table('oficiais')
    set_members_table('oficiais_superiores')
    set_members_table('corpo_executivo')
    set_members_table('corpo_executivo_superior')
    set_members_table('pracas')
    set_members_table('acesso_a_base')

    clear_atts_table('oficiais_atts')
    clear_atts_table('oficiais_superiores_atts')
    clear_atts_table('corpo_executivo_atts')
    clear_atts_table('corpo_executivo_superior_atts')
    clear_atts_table('pracas_atts')
    clear_atts_table('acesso_a_base_atts')
    