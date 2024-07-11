import sqlite3
import requests
from config.group_ids import *
from main import get_time

def get_group_member_list(group_id: str):
    _url = f'https://www.habbo.com.br/api/public/groups/{group_id}/members'
    request = requests.get(_url)

    group_members_list = []

    for member in request.json():
        group_members_list.append(
            {'nickname': member['name'].strip(), 'mission': member['motto'], 'isAdmin': member['isAdmin']}
        )

    return group_members_list



conn = sqlite3.connect('databsae.db')
cursor = conn.cursor()


def read_table(table_name, cursor=cursor):
    cursor.execute(f'SELECT * FROM {table_name}')
    
    table_output = cursor.fetchall()

    output_list = [{'nickname': profile[0], 'missao': profile[1], 'isAdmin': profile[2]} for profile in table_output]
    
    return output_list


def commit_changes(group_name, changes_dict, cursor=cursor):
    for member in changes_dict:
        cursor.execute(f'''
        INSERT INTO {group_name}_atts (nickname, status, date_time) VALUES (?, ?, ?)
        ''', (member['nickname'], member['status'], member['date_time']))
        
        conn.commit()


def check_changes(group_name, cursor=cursor):
    table_output = read_table(group_name)
    group_members = get_group_member_list(ID_OFICIAIS)
    
    
    group_changes = []
    
    for member in table_output:
        if member['nickname'] not in group_name:
            group_changes.append({'nickname': member['nickname'], 'status': 'saiu', 'date_time': get_time('%d/%m/%Y - %H:%M:00')})
    
    for member in group_members:
        if member['nickname'] not in table_output:
            group_changes.append({'nickname': member['nickname'], 'status': 'entrou', 'date_time': get_time('%d/%m/%Y - %H:%M:00')})
            
    
    if group_changes:
        commit_changes(group_name, group_changes)
    
    return


def remove_profile_from_db(profile_name, table_name, cursor=cursor):
    cursor.execute(f'''
    DELETE from {table_name}
    WHERE nickname = ?              
    ''', (profile_name,))
    
    return
    

check_changes('oficiais')
print(f'Alt: {read_table('oficiais_atts')}')
    
conn.commit()

conn.close()