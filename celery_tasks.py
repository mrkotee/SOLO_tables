
import os, time
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from openpyxl import load_workbook
try:
    from .models import base_path, VCode, Consigment, Collection, Table_row, path_for_old_base
    from .funcs import get_for_table, get_all_from_base, read_xlxs, add_boxes_to_vcodes, read_abc_xlxs
    from .solo_settings import xlxs_filepath, xlxs_abc_filepath
except:
    from models import base_path, VCode, Consigment, Collection, Table_row, path_for_old_base
    from funcs import get_for_table, get_all_from_base, read_xlxs, add_boxes_to_vcodes, read_abc_xlxs
    from solo_settings import xlxs_filepath, xlxs_abc_filepath




app = Celery('tasks', broker='redis://localhost:6379/0')


@app.task()
def update_base():
    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    xlxs_rows = read_xlxs(xlxs_filepath)

    changed_positions, rows_to_check, checked_rows, needed_collections = get_all_from_base(xlxs_rows, session)

    session.close()

    with open('update_result.txt', 'w') as f:
        for cllctn in needed_collections:
            f.write(cllctn + "\n")
        for change in changed_positions:
            f.write(change + "\n")


    new_path = path_for_old_base(update_time=True)
    os.system(r'cp {} {}'.format(base_path, new_path))


@app.task()
def del_return_docs_temp(filepath):
    time.sleep(15)
    os.remove(filepath)
