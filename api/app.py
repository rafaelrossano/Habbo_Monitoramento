import asyncio
import requests
import json
import threading


from flask import Flask, jsonify
from datetime import datetime
from pytz import timezone
from main import *
from db_functions import *


'''
############################################################
############################################################
####   ANTES DE RODAR APP.PY RODE O ARQUIVO CONFIG.PY  #####
############################################################
############################################################
'''


app = Flask(__name__)
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

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
    check_changes(group_name)
    return read_table(f'{group_name}_atts')


@app.route('/', methods=['GET'])
def index():
    return 'API Running...'


@app.route('/members/<group_name>', methods=['GET'])
def get_group_member_list_endpoint(group_name):
    return jsonify(handle_get_member_request(group_name))


@app.route('/atts/<group_name>', methods=['GET'])
def get_atts_endpoints(group_name:str):
    return jsonify(handle_get_atts_request(group_name))


if __name__ == '__main__':   
    
    app.run(host='0.0.0.0', port=5000, debug=True)
