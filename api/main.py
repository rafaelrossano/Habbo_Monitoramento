import requests
import json
import threading

from pytz import timezone
from datetime import datetime
from api.config.paths import *
from api.config.group_ids import *
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
def get_changes(log_file_name: str, log_file_check_name: str):
    log_file = open(log_file_name, 'r')
    log_file_check = open(log_file_check_name, 'r')

    group_last_check_members = []
    group_new_check_members = []

    for member_name in log_file:
        group_last_check_members.append(member_name)
    for member_name in log_file_check:
        group_new_check_members.append(member_name)

    changes_dict = []

    get_time("%d/%m/%Y - %H:%M:00")

    for name in group_last_check_members:
        if name not in group_new_check_members:
            changes_dict.append(
                {'nickname': name, 'status': 'saiu', 'datetime': get_time("%d/%m/%Y - %H:%M:00")}
            )

    for name in group_new_check_members:
        if name not in group_last_check_members:
            changes_dict.append(
                {'nickname': name, 'status': 'entrou', 'datetime': get_time("%d/%m/%Y - %H:%M:00")}
            )


    #write_log_file(log_file_name, log_file_check)


    log_file.close()
    log_file_check.close()

    return changes_dict


def check_change(changes_dict, atts_log_file):
    if changes_dict:
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
        

def main():
    sleep(5)
    
