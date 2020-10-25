import os
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from openpyxl import load_workbook
from .models import base_path, VCode, Consigment, Collection, Table_row, path_for_old_base
from .funcs import get_for_table, get_all_from_base, read_xlxs, add_boxes_to_vcodes, read_abc_xlxs
from .solo_settings import xlxs_filepath, xlxs_abc_filepath



def main(request, data_receved=False):
    last_update_time = 'Последнее обновление: '
    with open("last_update_time.txt", "r") as f:
        last_update_time += f.read()

    return render(request, 'solo_table.html', {
                                        'data_receved': data_receved,
                                        'last_update_time': last_update_time}
                                        )

def table(request):
    boxes_num = 0
    if request.method == 'GET':
        data = request.GET['data']

    elif request.method == 'POST':
        data = request.POST.get('data')
        boxes_num = request.POST.get('boxes_num')


    else:
        raise Http404

    data_list = data.split()

    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    if boxes_num:
        table_rows = get_for_table(data_list, session, boxes_num)
    else:
        table_rows = get_for_table(data_list, session)

    session.close()
    
    if request.method == 'GET':

        return HttpResponse(json.dumps(table_rows[0].__dict__), content_type="application/json")

    if request.method == 'POST':
        # return redirect('index', message_receved=True) #, {'page': 'index', 'message_receved': True})
        return render(request, 'solo_table.html', {'data_receved': True,
                                                'table_rows': table_rows,
                                                })


def update(request, file_receved=False):
    if request.method == 'POST':
        file = request.FILES['file']
        # fs = FileSystemStorage()
        # filename = fs.save(file.name, file)
        # uploaded_file_url = fs.url(filename)
        u_file = file.read()
        with open(xlxs_filepath, 'wb') as f:
            f.write(u_file)

        engine = create_engine('sqlite:///%s' % base_path, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            xlxs_rows = read_xlxs(xlxs_filepath)
        except Exception as e:
            return render(request, 'solo_update.html', {
                                        'wrong_file': True,
                                        })

        changed_positions, rows_to_check, checked_rows, needed_collections = get_all_from_base(xlxs_rows, session)

        session.close()

        with open('update_result.txt', 'w') as f:
            for cllctn in needed_collections:
                f.write(cllctn + "\n")
            for change in changed_positions:
                f.write(change + "\n")


        new_path = path_for_old_base(update_time=True)
        os.system(r'cp {} {}'.format(base_path, new_path))


        file_receved = True
        return render(request, 'solo_update.html', {
                                        'file_receved': file_receved,
                                        'changed_positions': changed_positions,
                                        'rows_to_check': rows_to_check,
                                        'checked_rows': checked_rows,
                                        'needed_collections': needed_collections,
                                        })


    with open('update_result.txt', 'r') as f:
        changed_positions = f.readlines()

    return render(request, 'solo_update.html', {
                                        'file_receved': file_receved,
                                        'changed_positions': changed_positions,
                                        })


def update_abc(request, file_receved=False):
    label = "ОБНОВЛЕНИЕ НОМЕНКЛАТУРЫ"
    if request.method == 'POST':

        file = request.FILES['file']
        u_file = file.read()
        with open(xlxs_abc_filepath, 'wb') as f:
            f.write(u_file)

        engine = create_engine('sqlite:///%s' % base_path, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            xlxs_rows = read_abc_xlxs(xlxs_abc_filepath)
        except Exception as e:
            return render(request, 'solo_update.html', {
                                        'label': label,
                                        'wrong_file': True,
                                        })

        changed_positions = add_boxes_to_vcodes(xlxs_rows, session)

        session.close()

        with open('update_abc_result.txt', 'w') as f:
            for change in changed_positions:
                f.write(change + "\n")


        new_path = path_for_old_base(update_time=True)
        os.system(r'cp {} {}'.format(base_path, new_path))


        file_receved = True
        return render(request, 'solo_update.html', {
                                        'label': label,
                                        'file_receved': file_receved,
                                        'changed_positions': changed_positions,
                                        })


    with open('update_abc_result.txt', 'r') as f:
        changed_positions = f.readlines()

    return render(request, 'solo_update.html', {
                                        'label': label,
                                        'file_receved': file_receved,
                                        'changed_positions': changed_positions,
                                        })
