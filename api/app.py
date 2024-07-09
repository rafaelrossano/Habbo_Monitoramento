from flask import Flask, jsonify
from datetime import datetime
from pytz import timezone
from paths import *
from group_ids import *

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
    with open(file_path, 'w+') as log_file:
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
    
write_log_file(, get_group_member_list(ID_CORPO_EXECUTIVO))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
