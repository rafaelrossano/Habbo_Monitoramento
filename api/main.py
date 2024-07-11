import requests
import json
import threading

from pytz import timezone
from datetime import datetime
from config.paths import *
from config.group_ids import *
from time import sleep


def get_time(datetime_format: str):
    now = datetime.now()
    fz = timezone("America/Sao_Paulo")

    now = now.astimezone(fz)
    trp = now.strftime(datetime_format)

    return trp


# Argument - Group Unique Id
# Return - ['Name', 'Name', ...]
def get_group_member_list(group_id: str):
    _url = f'https://www.habbo.com.br/api/public/groups/{group_id}/members'
    request = requests.get(_url)

    group_members_list = []

    for member in request.json():
        group_members_list.append(
            {'nickname': member['name'].strip(), 'mission': member['motto'], 'isAdmin': member['isAdmin']}
        )

    return group_members_list


def write_log_file(file_path: str, group_members_list: list):
    with open(file_path, 'w+', encoding='utf-8') as log_file:
        json.dump(group_members_list, log_file, indent=4)


def write_changes_file(file_path: str, group_members_list: list):
    with open(file_path, 'a', encoding='utf-8') as changes_file:
        json.dump(group_members_list, changes_file, indent=4)

# Check two files: log_file_name, that contains an "old" members list
# and check log_file_check_name, containing a new member list to compare between them

# Return two dictionaries: joined_groups and left_groups
# {'name': 'Nickname', 'status': 'entrou/saiu', 'datetime': '%d/%m/%Y - %H:%M:00'
def get_changes(log_file_name: str, log_file_check_name: str, txt_file_path: str):
    log_file = open(log_file_name, 'r', encoding='utf-8')
    log_file_check = open(log_file_check_name, 'r', encoding='utf-8')
    txt_file_path = open(txt_file_path, 'a+', encoding='utf-8')
    
    last_check_data = json.load(log_file)
    new_check_data = json.load(log_file_check)
    
    
    last_check_list = []
    new_check_list = []
    
    
    changes_dict = []
    
    
    for json_entry in last_check_data:
        last_check_list.append(json_entry['nickname'])
        
    for json_entry in new_check_data:
        new_check_list.append(json_entry['nickname'])
        
    
    date_time = get_time('%d/%m/%Y - %H:%M:00')
        
    
    for group_member in last_check_list:
        if group_member not in new_check_list:
           txt_file_path.write(f'nickname: {group_member}, status: entrou, datetime: {date_time}\n')
            
    for group_member in new_check_list:
        if group_member not in last_check_list:
            txt_file_path.write(f'nickname: {group_member}, status: saiu, datetime: {date_time}\n')
            
    
    txt_file_path.seek(0)
    
    print(txt_file_path.read())     
    
    for line in txt_file_path:
            # Remover espaços em branco no início e no fim da linha
            line = line.strip()

            # Ignorar linhas vazias
            if not line:
                continue

            # Dividir a linha em partes
            parts = line.split(", ")
            nickname = parts[0].split(": ")[1]
            status = parts[1].split(": ")[1]
            datetime = parts[2].split(": ")[1]

            # Adicionar ao dicionário
            changes_dict_in = {
                'nickname': nickname,
                'status': status,
                'datetime': datetime
            }
            changes_dict.append(changes_dict_in)
            
    print(changes_dict)
            
    log_file.close()
    log_file_check.close()
    
    return changes_dict


def check_change(changes_dict, atts_log_file):
    changes_dict = changes_dict
    print('oi')
    if len(changes_dict) > 0:
        with open(atts_log_file, 'a') as atts_log_file:
            json.dump(changes_dict, atts_log_file, indent=4)
    return


def handle_atts(group_name):
    
    if group_name == 'oficiais':
        check_change(get_changes(OFICIAIS_MEMBROS_PATH, OFICIAIS_CHECK_PATH), OFICIAIS_ATTS_PATH)
        with open(OFICIAIS_ATTS_PATH, 'r', encoding='utf-8') as json_file: 
            return json.load(json_file)

    if group_name == 'oficiais_superiores':
        check_change(get_changes(OFICIAIS_SUPERIORES_MEMBROS_PATH, OFICIAIS_SUPERIORES_CHECK_PATH), OFICIAIS_SUPERIORES_ATTS_PATH)
        with open(OFICIAIS_SUPERIORES_ATTS_PATH, 'r', encoding='utf-8') as json_file: 
            return json.load(json_file)
        
    if group_name == 'corpo_executivo':
        check_change(get_changes(CORPO_EXECUTIVO_MEMBROS_PATH, CORPO_EXECUTIVO_CHECK_PATH), CORPO_EXECUTIVO_ATTS_PATH)
        with open(CORPO_EXECUTIVO_ATTS_PATH, 'r', encoding='utf-8') as json_file: 
            return json.load(json_file)
        
    if group_name == 'corpo_executivo_superior':
        check_change(get_changes(CORPO_EXECUTIVO_SUPERIOR_MEMBROS_PATH, CORPO_EXECUTIVO_SUPERIOR_CHECK_PATH), CORPO_EXECUTIVO_SUPERIOR_ATTS_PATH)
        with open(CORPO_EXECUTIVO_SUPERIOR_ATTS_PATH, 'r', encoding='utf-8') as json_file: 
            return json.load(json_file)
        
    if group_name == 'pracas':
        check_change(get_changes(PRACAS_MEMBROS_PATH, PRACAS_CHECK_PATH), PRACAS_ATTS_PATH)
        with open(PRACAS_ATTS_PATH, 'r', encoding='utf-8') as json_file: 
            return json.load(json_file)
        
    if group_name == 'acesso_a_base':
        check_change(get_changes(ACESSO_A_BASE_MEMBROS_PATH, ACESSO_A_BASE_CHECK_PATH), ACESSO_A_BASE_ATTS_PATH)
        with open(ACESSO_A_BASE_ATTS_PATH, 'r', encoding='utf-8') as json_file: 
            return json.load(json_file)
        

def check_oficiais():
    group_member_list = get_group_member_list(ID_OFICIAIS)
    write_log_file(OFICIAIS_CHECK_PATH, group_member_list)
    groups_dict = get_changes(OFICIAIS_MEMBROS_PATH, OFICIAIS_CHECK_PATH, OFICIAIS_TXT_PATH)
    check_change(groups_dict, OFICIAIS_ATTS_PATH)
    write_log_file(OFICIAIS_MEMBROS_PATH, group_member_list)
    


def main():
    check_oficiais()


if __name__ == '__main__':
    main()