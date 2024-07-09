from app import write_log_file, get_group_member_list
from api.config.group_ids import *
from api.config.paths import *


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