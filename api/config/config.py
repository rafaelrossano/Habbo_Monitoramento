from group_ids import *
from paths import *

import requests
import json

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


try:
    # OFICIAIS
    write_log_file(OFICIAIS_MEMBROS_PATH, get_group_member_list(ID_OFICIAIS))

    # OFICIAIS SUPERIORES
    write_log_file(OFICIAIS_SUPERIORES_MEMBROS_PATH, get_group_member_list(ID_OFICIAIS_SUPERIORES))

    # CORPO EXECUTIVO
    write_log_file(CORPO_EXECUTIVO_MEMBROS_PATH, get_group_member_list(ID_CORPO_EXECUTIVO))

    # CORPO EXECUTIVO SUPERIOR
    write_log_file(CORPO_EXECUTIVO_SUPERIOR_MEMBROS_PATH, get_group_member_list(ID_CORPO_EXECUTIVO_SUPERIOR))

    # PRACAS
    write_log_file(PRACAS_MEMBROS_PATH, get_group_member_list(ID_PRACAS))

    # ACESSO A BASE
    write_log_file(ACESSO_A_BASE_MEMBROS_PATH, get_group_member_list(ID_PRACAS))
    
    print('Initial files successfully configured!')
    
except Exception:
    print('Error configuring initial files. :' + Exception)