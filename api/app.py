from flask import Flask, jsonify
from datetime import datetime
from pytz import timezone

import contextlib
import requests
import json


app = Flask(__name__)


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
            {'nickname': member['name'].strip(), 'motto': member['motto'], 'isAdmin': member['isAdmin']}
        )

    return group_members_list


def write_log_file(file_path: str, group_members_list: list):
    with open(file_path, 'w') as log_file:
        json.dump(group_members_list, log_file, indent=4)


# Check two files: log_file_name, that contains an "old" members list
# and check log_file_check_name, containing a new member list to compare between them

# Return two dictionaries: joined_groups and left_groups
# {'name': 'Nickname', 'status': 'entrou/saiu', 'datetime': '%d/%m/%Y - %H:%M:00'
def check_changes(log_file_name: str, log_file_check_name: str):
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

    log_file.close()
    log_file_check.close()

    return changes_dict


ID_OFICIAIS = 'g-hhbr-247773992b2ed79b8f00e564abad2c43'
ID_OFICIAIS_SUPERIORES = 'g-hhbr-7b5c62e80d30cd30f003eab08555a124'
ID_PRACAS = 'g-hhbr-e45543b627d203d8caf1a4476bb42fab'
ID_CORPO_EXECUTIVO = 'g-hhbr-da0cd92560170f5d42d0e59dd6dbc268'
ID_CORPO_EXECUTIVO_SUPERIOR = 'g-hhbr-7f9e61c9ce3700323d870bf420732535'


paths = [
    {'corpo_executivo_membros': 'logs/corpo_executivo/corpo_executivo_membros.json'},
    {'corpo_executivo_check': 'logs/corpo_executivo/corpo_executivo_check.json'},
    {'corpo_executivo_atts': 'logs/corpo_executivo/corpo_executivo_atts.json'},
    {'corpo_executivo_superior_membros': 'logs/corpo_executivo_superior/corpo_executivo_superior_membros.json'},
    {'corpo_executivo_superior_check': 'logs/corpo_executivo_superior/corpo_executivo_superior_check.json'},
    {'corpo_executivo_superior_atts': 'logs/corpo_executivo_superior/corpo_executivo_superior_atts.json'},
    {'oficiais_membros': 'logs/oficiais/oficiais_membros.json'},
    {'oficiais_check': 'logs/oficiais/oficiais_check.json'},
    {'oficiais_atts': 'logs/oficiais/oficiais_atts.json'},
    {'oficiais_superiores_membros': 'logs/oficiais_superiores_membros.json'},
    {'oficiais_superiores_check': 'logs/oficiais_superiores/oficiais_superiores_check.json'},
    {'oficiais_superiores_atts': 'logs/oficiais_superiores/oficiais_superiores_atts.json'},
    {'pracas_membros': 'logs/pracas/pracas_membros.json'},
    {'pracas_check': 'logs/pracas/pracas_check.json'},
    {'pracas_atts': 'logs/pracas/pracas_atts.json'},
    {'acceso_a_base_membros': 'logs/acceso_a_base/acceso_a_base_membros.json'},
    {'acceso_a_base_check': 'logs/acceso_a_base/acceso_a_base_check.json'},
    {'acesso_a_base_atts': 'logs/acesso_a_base/acesso_a_base_atts.json'},
]


def get_members_oficiais():
    group_members_list = get_group_member_list(ID_OFICIAIS)
    return jsonify(group_members_list)


def handle_get_member_request(group_name: str):

    if group_name == 'oficiais':
        return get_members_oficiais()
    #if group_name == 'oficiais_superiores': return get_members_oficiais_superiores()


@app.route('/', methods=['GET'])
def index():
    return 'API Running...'


#@app.route('/members/<group_name>', methods=['GET'])
#def get_group_member_list(group_name: str):
    #return jsonify(get_group_member_list(group_name))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
