import os
from django.http import Http404, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from openpyxl import load_workbook
from .models import base_path, VCode, Consigment, Collection, Table_row, path_for_old_base
from .funcs import get_for_table, get_all_from_base, read_xlxs, add_boxes_to_vcodes, read_abc_xlxs
from .solo_settings import xlxs_filepath, xlxs_abc_filepath, docs_temp_dir
from .celery_tasks import update_base, del_return_docs_temp
from .contract_funcs import create_contract
from .return_doc_funcs import get_doc_of_return
from .return_doc_funcs import read_xlxs as read_return_doc_xlxs



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
    uni_boxes_num = 0
    get_all_consigs = False
    if request.method == 'GET':
        data = request.GET['data']

    elif request.method == 'POST':
        data = request.POST.get('data')
        boxes_num = request.POST.get('boxes_num')
        uni_boxes_num = request.POST.get('uni_boxes_num')
        get_all_consigs = request.POST.get('get_all_consigs')

    else:
        raise Http404

    if get_all_consigs:
        get_all_consigs = True
    else:
        get_all_consigs = False

    data_list = data.split()

    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    if boxes_num:
        if uni_boxes_num:
            table_rows = get_for_table(data_list, session, 
                                        boxes_num, uni_boxes_num,
                                        get_all_consigs)
        else:
            table_rows = get_for_table(data_list, session, 
                                    boxes_num, get_all_consigs)
    elif uni_boxes_num:
        table_rows = get_for_table(data_list, session, 
                                    get_all_consigs, 
                                    uni_boxes_num=uni_boxes_num)
    else:
        table_rows = get_for_table(data_list, session, get_all_consigs)

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
        u_file = file.read()
        with open(xlxs_filepath, 'wb') as f:
            f.write(u_file)


        try:
            xlxs_rows = read_xlxs(xlxs_filepath)
        except Exception as e:
            return render(request, 'solo_update.html', {
                                        'wrong_file': True,
                                        })

        update_base.delay()
        changed_positions = ["Update will be done soon"]



        file_receved = True
        return render(request, 'solo_update.html', {
                                        'file_receved': file_receved,
                                        'changed_positions': changed_positions,
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



def contract(request):

    if request.method == 'GET':
        return render(request, 'contract.html', {}
                                        )
    elif request.method == 'POST':
        firm_type = request.POST.get('firm_type')
        second_firm = request.POST.get('second_firm')
        credit_limit = request.POST.get('credit_limit')
        firm_name = request.POST.get('firm_name')
        position = request.POST.get('position')
        name = request.POST.get('name')
        director = request.POST.get('director')
        document = request.POST.get('document')
        kpp = request.POST.get('kpp')
        ogrnip = request.POST.get('ogrnip')
        gender = int(request.POST.get('gender'))
        pers_id_series = request.POST.get('pers_id_series')
        pers_id_number = request.POST.get('pers_id_number')
        pers_id_gover = request.POST.get('pers_id_gover')
        firm_id = request.POST.get('firm_id')
        post_address = request.POST.get('post_address')
        firm_address = request.POST.get('firm_address')
        current_account = request.POST.get('current_account')
        corr_account = request.POST.get('corr_account')
        bank_bik = request.POST.get('bank_bik')
        bank_name = request.POST.get('bank_name')

        if director:
            name = director
            
        contract_filename, contract_filepath = create_contract(firm_type,
                        second_firm, 
                        position,
                        firm_name,
                        name,
                        document,
                        credit_limit,
                        post_address,
                        firm_address,
                        firm_id,
                        kpp,
                        current_account,
                        bank_name,
                        corr_account,
                        bank_bik,
                        ogrnip,
                        gender,
                        pers_id_series,
                        pers_id_number,
                        pers_id_gover)

        return redirect('/solo/contracts/%s' % contract_filename)
        # response = HttpResponse(FileResponse(open(contract_filepath, 'rb')), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        # response['Content-Disposition'] = 'attachment; filename*=UTF-8"%s"' % contract_filename
        # return response
        # return HttpResponse(json.dumps(result), content_type="application/json")
        # return HttpResponse(json.dumps((firm_type,
        #                                 second_firm,
        #                                 credit_limit,
        #                                 position,
        #                                 name,
        #                                 director,
        #                                 document,
        #                                 kpp,
        #                                 ogrnip,
        #                                 gender,
        #                                 pers_id_series,
        #                                 pers_id_number,
        #                                 pers_id_gover,
        #                                 firm_id,
        #                                 post_address,
        #                                 firm_address,
        #                                 current_account,
        #                                 corr_account,
        #                                 bank_bik,
        #                                 bank_name)), content_type="application/json")


def return_docs(request):

    if request.method == 'GET':
        return render(request, 'return_docs.html', {'text': 'test'}
                                        )
    elif request.method == 'POST':
        file = request.FILES['file']
        u_file = file.read()

        temp_filepath = docs_temp_dir + '{}.xlsx'.format(request.session.session_key)
        with open(temp_filepath, 'wb') as f:
            f.write(u_file)


        try:
            positions = read_return_doc_xlxs(xlxs_filepath)
        except Exception as e:
            return render(request, 'return_docs.html', {
                                        'file_receved': file_receved,
                                        'wrong_file': True,
                                        })

        nds = request.POST.get('nds')
        if nds:
            nds = True
        else:
            nds = False

        data = request.POST.get('data')
        data_list = data.split()


        engine = create_engine('sqlite:///%s' % base_path, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        return_vcodes_dict = {}
        for table_row in get_for_table(data_list, session):
            return_vcodes_dict[str(table_row.vcode)] = table_row.number

        session.close()

        filename = 'возврат {}.xlsx'.format(' '.join(return_vcodes_dict.keys()))
        save_to = docs_temp_dir + filename

        get_doc_of_return(temp_filepath, return_vcodes_dict, save_to, nds)

        del_return_docs_temp.delay(temp_filepath)
        del_return_docs_temp.delay(save_to)

        return redirect('/solo/r_docs/%s' % filename)

        file_receved = True
        return render(request, 'return_docs.html', {
                                        'file_receved': file_receved,
                                        })
