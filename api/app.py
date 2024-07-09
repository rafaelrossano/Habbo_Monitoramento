import asyncio
import requests
import json
import threading


from flask import Flask, jsonify
from datetime import datetime
from pytz import timezone
from main import *


'''
############################################################
############################################################
####   ANTES DE RODAR APP.PY RODE O ARQUIVO CONFIG.PY  #####
############################################################
############################################################
'''


app = Flask(__name__)


def handle_get_member_request(group_name: str):

    if group_name == 'oficiais':
        return get_group_member_list(ID_OFICIAIS)
    if group_name == 'oficiais_superiores':
        return get_group_member_list(ID_OFICIAIS_SUPERIORES)
    if group_name == 'corpo_executivo':
        return get_group_member_list(ID_CORPO_EXECUTIVO)
    if group_name == 'corpo_executivo_superior':
        return get_group_member_list(ID_CORPO_EXECUTIVO_SUPERIOR)
    if group_name == 'acesso_a_base':
        return get_group_member_list(ID_ACESSO_A_BASE)
    if group_name == 'pracas':
        return get_group_member_list(ID_PRACAS)
    

def handle_get_atts_request(group_name: str):
    
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


@app.route('/', methods=['GET'])
def index():
    return 'API Running...'


@app.route('/members/<group_name>', methods=['GET'])
def get_group_member_list_endpoint(group_name):
    return jsonify(handle_get_member_request(group_name))


@app.route('/atts/<group_name>', methods=['GET'])
def get_atts_endpoints(group_name:str):
    return handle_get_atts_request(group_name)


if __name__ == '__main__':   
    
    app.run(host='0.0.0.0', port=5000, debug=True)
