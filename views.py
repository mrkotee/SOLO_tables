from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime as dt
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .alchemy_models import base_path
from .alchemy_models import Factory, MailAddress
from .funcs.funcs import get_for_table, read_xlxs, read_abc_xlxs
from .solo_settings import xlxs_filepath, xlxs_abc_filepath, docs_temp_dir, sng_base_path
from .solo_settings import name_base_path, mail_set_base_path
from .funcs.celery_tasks import update_base, del_return_docs_temp
from .funcs.celery_tasks import update_abc as cel_update_abc
from .funcs.contract_funcs import create_contract, create_addition_contract
from .return_doc_funcs import get_doc_of_return
from .return_doc_funcs import read_xlxs as read_return_doc_xlxs
from .sng.sng_funcs import read_xlxs as read_sng_xlxs
from .sng.sng_funcs import add_names_to_base, change_names_xlxs
from .sng.sng_models import Clients_row, Client


def create_session(_base_path):
    engine = create_engine('sqlite:///%s' % _base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def main(request, data_receved=False):
    last_update_time = 'Последнее обновление: '
    try:
        with open("last_update_time.txt", "r") as f:
            last_update_time += f.read()
    except FileNotFoundError:
        last_update_time += "Еще не обновляли"

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

    session = create_session(base_path)
    if boxes_num:
        if uni_boxes_num:
            table_rows = get_for_table(data_list, session, 
                                        boxes_num, uni_boxes_num,
                                        get_all_consigs=get_all_consigs)
        else:
            table_rows = get_for_table(data_list, session, 
                                    boxes_num, get_all_consigs=get_all_consigs)
    elif uni_boxes_num:
        table_rows = get_for_table(data_list, session, 
                                    get_all_consigs=get_all_consigs,
                                    uni_boxes_num=uni_boxes_num)
    else:
        table_rows = get_for_table(data_list, session, get_all_consigs=get_all_consigs)

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

    try:
        with open('update_result.txt', 'r') as f:
            changed_positions = f.readlines()
    except FileNotFoundError:
        changed_positions = ["Обновлений не было"]

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


        cel_update_abc.delay()
        changed_positions = ["Update will be done soon"]


        try:
            xlxs_rows = read_abc_xlxs(xlxs_abc_filepath)
        except Exception as e:
            return render(request, 'solo_update.html', {
                'label': label,
                'wrong_file': True,
            })


        file_receved = True
        return render(request, 'solo_update.html', {
            'label': label,
            'file_receved': file_receved,
            'changed_positions': changed_positions,
        })

    try:
        with open('update_abc_result.txt', 'r') as f:
            changed_positions = f.readlines()
    except FileNotFoundError:
        changed_positions = ["Обновлений не было"]

    return render(request, 'solo_update.html', {
        'label': label,
        'file_receved': file_receved,
        'changed_positions': changed_positions,
    })


def contract(request):
    if request.method == 'GET':
        return render(request, 'contract.html', {'date_today': dt.strftime(dt.now().date(), "%Y-%m-%d")}
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
        contract_number = request.POST.get('contract_number')
        date_contract = request.POST.get('date_contract')
        form_type = request.POST.get('form_type')

        if director:
            name = director
            
        if 'соглашение' in form_type:
            _date_contract = dt.strptime(date_contract, "%Y-%m-%d")
            contract_filename, contract_filepath = create_addition_contract(
                firm_type,
                position,
                firm_name,
                name,
                document,
                ogrnip,
                gender,
                date_contract=_date_contract,
                contract_number=contract_number,)

        else:
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
        return render(request, 'return_docs.html', {}
                      )
    elif request.method == 'POST':
        file = request.FILES['file']
        u_file = file.read()

        temp_filepath = docs_temp_dir + '{}.xlsx'.format(request.session.session_key)
        with open(temp_filepath, 'wb') as f:
            f.write(u_file)

        try:
            positions = read_return_doc_xlxs(temp_filepath)
        except Exception as e:
            return render(request, 'return_docs.html', {
                                        'file_receved': True,
                                        'wrong_file': True,
                                        })

        nds = request.POST.get('nds')
        if nds:
            nds = True
        else:
            nds = False

        data = request.POST.get('data')
        data_list = data.split()

        if not data_list:
            # return HttpResponse(json.dumps((data_list, positions, nds, temp_filepath)), content_type="application/json")
            data_list = []
            for pos in positions:
                data_list.append(str(pos['vcode']))
                data_list.append(str(pos['number']))

        session = create_session(base_path)

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


def change_names(request):

    if request.method == 'GET':
        session = create_session(sng_base_path)

        clients_rows = [Clients_row(cl.id, cl.name) for cl in session.query(Client).all()]

        session.close()
        return render(request, 'change_names.html', {'clients_rows': clients_rows}
                                        )
    elif request.method == 'POST':
        file = request.FILES['file']
        u_file = file.read()

        add_to_base = request.POST.get('add_new')
        client = request.POST.get('client')
        client_new = request.POST.get('client_new')

        if client == 'Выберите клиента':
            client = None
        if client_new:
            client = client_new


        temp_filepath = docs_temp_dir + '{}.xlsx'.format(request.session.session_key)
        with open(temp_filepath, 'wb') as f:
            f.write(u_file)


        session = create_session(sng_base_path)

        if add_to_base or not client:
            data = read_sng_xlxs(temp_filepath)
            if client:
                add_names_to_base(session, data, client)
            else:
                add_names_to_base(session, data)

            clients_rows = [Clients_row(cl.id, cl.name) for cl in session.query(Client).all()]
            session.close()

            return render(request, 'change_names.html', {'clients_rows': clients_rows}
                                        )

        else:
            filename = 'книга1.xlsx'
            save_to = docs_temp_dir + filename

            change_names_xlxs(session, temp_filepath, save_to, client)

            del_return_docs_temp.delay(temp_filepath)
            del_return_docs_temp.delay(save_to)


            session.close()

            return redirect('/solo/r_docs/%s' % filename)


def settings_page(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return render(request, 'solo_settings.html', {
            })
        http_ref = request.META.get("HTTP_REFERER", request.path)
        session = create_session(base_path)
        names_session = create_session(name_base_path)
        mail_session = create_session(mail_set_base_path)

        factories = names_session.query(Factory).order_by(Factory.actual.desc()).all()

        mails = mail_session.query(MailAddress).all()

        session.close()
        names_session.close()
        mail_session.close()
        return render(request, 'solo_settings.html', {
            "fabrics": factories,
            "emails": mails,
        })
    elif request.is_ajax():
        if not request.user.is_authenticated:
            raise Http404

        command = request.POST.get('cmd')
        if command == "get":
            need_data = request.POST.get('need_data')
            pass
        elif command == "edit":
            value_type = request.POST.get('type')
            object_name = request.POST.get('name')
            value = request.POST.get('value')
            if value == "active":
                value = True
            elif value == "inactive":
                value = False

            response = {'resp': 'ok'}
            if value_type == 'fabric':
                names_session = create_session(name_base_path)
                factory = names_session.query(Factory).filter(Factory.name == object_name).first()
                if factory:
                    factory.actual = value

                    names_session.commit()

                    response["name"] = factory.name
                else:
                    response['resp'] = 'None'
                names_session.close()

            elif value_type == "email":
                value_type = request.POST.get('value_type')
                mail_session = create_session(mail_set_base_path)
                email_obj = mail_session.query(MailAddress).filter(
                    MailAddress.email == object_name).first()

                """possible names: 'marrys', 'main', 'edit' """
                if value_type == "main":
                    email_obj.is_main = value
                    print(email_obj.email)
                    print(value)

                elif value_type == "marrys":
                    email_obj.in_marrys_list = value

                elif value_type == "edit":
                    pass

                mail_session.commit()
                mail_session.close()

            return JsonResponse(response)
    # elif request.method == 'POST':

    raise Http404
