
import os, time
import base64
from datetime import datetime as dt
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from openpyxl import load_workbook
try:
    from models import base_path, VCode, Consigment, Collection, Table_row, \
    path_for_old_base, name_base_path
    from funcs import get_for_table, get_all_from_base, read_xlxs, \
    add_boxes_to_vcodes, read_abc_xlxs, add_names_to_vcodes, separate_by_factories, create_xlsx_without_consigments
    from solo_settings import xlxs_filepath, xlxs_abc_filepath, sep_files_dir
    from funcs import create_amounts_to_mary
    from funcs import send_mails_smtp as send_mails
    from m_settings import mail_list, marys_mail, smtp_server, smtp_from, mail_text
except:
    from solo.models import base_path, VCode, Consigment, Collection, Table_row, \
    path_for_old_base, name_base_path
    from .funcs import get_for_table, get_all_from_base, read_xlxs, \
    add_boxes_to_vcodes, read_abc_xlxs, add_names_to_vcodes, separate_by_factories, create_xlsx_without_consigments
    from solo.solo_settings import xlxs_filepath, xlxs_abc_filepath, sep_files_dir
    from .funcs import create_amounts_to_mary
    from .funcs import send_mails_smtp as send_mails
    from solo.m_settings import mail_list, marys_mail, smtp_server, smtp_from, mail_text




app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task()
def update_base():
    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    xlxs_rows = read_xlxs(xlxs_filepath)

    changed_positions, rows_to_check, checked_rows, needed_collections = get_all_from_base(xlxs_rows, session)


    with open('update_result.txt', 'w') as f:
        for cllctn in needed_collections:
            f.write(cllctn + "\n")
        for change in changed_positions:
            f.write(change + "\n")


    new_path = path_for_old_base(update_time=True)
    os.system(r'cp {} {}'.format(base_path, new_path))

    n_engine = create_engine('sqlite:///%s' % name_base_path, echo=False, poolclass=QueuePool)
    n_Session = sessionmaker(bind=n_engine)
    n_session = n_Session()

    global sep_files_dir

    separate_by_factories(sep_files_dir, session, n_session)


    if dt.now().hour < 10 and dt.now().hour > 7:
        send_mails(sep_files_dir, smtp_from, smtp_server, mail_list, text=mail_text)
    else:
        send_mails(sep_files_dir, smtp_from, smtp_server, [mail_list[0]], text=mail_text)

    ############## mary ###########
    for f in os.listdir(sep_files_dir):
        os.remove(os.path.join(sep_files_dir, f))

    create_xlsx_without_consigments(sep_files_dir, session)
    create_amounts_to_mary(sep_files_dir, session)


    if dt.now().hour < 10 and dt.now().hour > 7:
        send_mails(sep_files_dir, smtp_from, smtp_server, marys_mail, mary=True, text=mail_text)
    else:
        send_mails(sep_files_dir, smtp_from, smtp_server, [mail_list[0]], mary=True, text=mail_text)

    ###############################
    session.close()
    n_session.close()
    
    for f in os.listdir(sep_files_dir):
        os.remove(os.path.join(sep_files_dir, f))



@app.task()
def del_return_docs_temp(filepath):
    time.sleep(15)
    os.remove(filepath)


@app.task()
def update_abc():


    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    xlxs_rows = read_abc_xlxs(xlxs_abc_filepath)

    changed_positions = add_boxes_to_vcodes(xlxs_rows, session)

    session.close()

    with open('update_abc_result.txt', 'w') as f:
        for change in changed_positions:
            f.write(change + "\n")


    # new_path = path_for_old_base(update_time=True)
    # os.system(r'cp {} {}'.format(base_path, new_path))

    engine = create_engine('sqlite:///%s' % name_base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    changed_positions = add_names_to_vcodes(xlxs_rows, session)

    session.close()

    with open('update_abc_result.txt', 'a') as f:
        for change in changed_positions:
            f.write(change + "\n")
