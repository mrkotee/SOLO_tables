import os
from datetime import datetime as dt
from docxtpl import DocxTemplate
import pymorphy2
try:
    from .num2str import num2text
    from .solo_settings import mounth_names, solo_path
except:
    from num2str import num2text
    from solo_settings import mounth_names, solo_path




def create_contract(
    firm_type,
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
    pers_id_gover):

    morph = pymorphy2.MorphAnalyzer()

    def morph_word(word_string, morph_set, its_name=True):
        result_string = ''
        for _word in word_string.split():
            parsed = morph.parse(_word)
            word = None
            if len(parsed) > 1 and its_name:
                for _w in parsed:
                    if 'Sgtm' in _w.tag:
                        word = _w
            if not word:
                word = parsed[0]

            result_string += word.inflect(morph_set).word + ' '
        return result_string


    filename = ''
    result_filename_list = ['', '', '', '']
    if int(second_firm) == 2:
        filename += 'solo_decor_'
        result_filename_list[3] = 'Соло Декор'
    else:
        filename += 'alians_decor_'
        result_filename_list[3] = 'Альянс Декор'

    if int(firm_type) == 2:
        filename += 'u_l_'
        firm_type = "Общество с ограниченной ответственностью"
        result_filename_list[0] = 'ООО'
        result_filename_list[1] = firm_name.title()
    else:
        filename += 'ip_'
        firm_type = "Индивидуальный предприниматель"
        result_filename_list[0] = 'ИП'

    if credit_limit:
        filename += 'otsrochka.docx'
        credit_limit = int(credit_limit)
        result_filename_list[2] = '%d дней' % credit_limit
    else:
        filename += 'predoplata.docx'
        result_filename_list[2] = 'предоплата'

    word_path = os.path.join(solo_path, 'word_templates', filename)

    ###########################


    firm_name = '«' + firm_name.title() + '»'
    firm_type = firm_type.capitalize()
    full_firm_name = firm_type + ' ' + firm_name
    date_today = '«{:02d}» {} {} '.format(dt.now().day, mounth_names[dt.now().month], dt.now().year)
    if 'solo_decor' in word_path:
        date_today += 'г.'
    expire_date = '«{:02d}» {} {} года'.format(dt.now().day, mounth_names[dt.now().month], dt.now().year+3)

    position_1 = morph_word(position, {'sing', 'gent'}, its_name=False)
    if 'u_l' in word_path:
        director = morph_word(name, {'sing', 'gent'}, its_name=True)
    else:
        director = name
    # document = morph_word(document)

    director_short = ''
    for i, w in enumerate(name.split()):
        if i != 0:
            w = w[0] + '.'
        else:
            w = w + ' '
        director_short += w

    if credit_limit:
        credit_limit = '{} ({})'.format(credit_limit, morph_word(num2text(credit_limit), {'gent'}, its_name=False).rstrip())  ## добавить календарных дней
        if 'solo_decor_u' in word_path:
            credit_limit += ' календарных дней'
        elif 'solo_decor_ip' in word_path:
            credit_limit += ' календарных'
        elif 'alians' in word_path:
            pass

    if gender == 2:
        gender = 'именуемая'
    else:
        gender = 'именуемый'

    ############ work with word file ###############


    doc = DocxTemplate(word_path)

    context = {
        'date_today': date_today,
        'full_firm_name': full_firm_name,
        'firm_name': firm_name,
        'director': director.title().rstrip(),
        'director_short': director_short.title(),
        'position_1': position_1.capitalize(),
        'position_2': position.capitalize(),
        'document': document.capitalize(),
        'delivery_1': '',
        'delivery_2': 'X',
        'delivery_2_address': 'г. Москва',
        'delivery_3': '',
        'credit_limit': credit_limit,
        'post_address': post_address,
        'expire_date': expire_date,
        'firm_address': firm_address,
        'firm_id': firm_id,
        'kpp': kpp,
        'current_account': current_account,
        'bank_name': bank_name,
        'corr_account': corr_account,
        'BIK': bank_bik,
        'ogrnip': ogrnip,
        'gender': gender,
        'pers_id_series': pers_id_series,
        'pers_id_number': pers_id_number,
        'pers_id_gover': pers_id_gover,

    }
    doc.render(context)

    if firm_type == "Индивидуальный предприниматель":
        result_filename_list[1] = director_short

    result_filename = ' '.join(result_filename_list) + '.docx'
    save_path = os.path.join(solo_path, 'contracts', result_filename)
    doc.save(save_path)
    return result_filename, save_path


def create_addition_contract(
    firm_type,
    position,
    firm_name,
    name,
    document,
    ogrnip,
    gender,
    credit_limit=90,):

    morph = pymorphy2.MorphAnalyzer()

    def morph_word(word_string, morph_set, its_name=True):
        result_string = ''
        for _word in word_string.split():
            parsed = morph.parse(_word)
            word = None
            if len(parsed) > 1 and its_name:
                for _w in parsed:
                    if 'Sgtm' in _w.tag:
                        word = _w
            if not word:
                word = parsed[0]

            result_string += word.inflect(morph_set).word + ' '
        return result_string


    filename = ''
    result_filename_list = ['', '', '', '']

    filename += 'alians_decor_catalogs_'
    result_filename_list[3] = 'Альянс Декор'

    if int(firm_type) == 2:
        filename += 'u_l'
        firm_type = "Общество с ограниченной ответственностью"
        result_filename_list[0] = 'ООО'
        result_filename_list[1] = firm_name.title()
    else:
        filename += 'ip'
        firm_type = "Индивидуальный предприниматель"
        result_filename_list[0] = 'ИП'

    filename += '.docx'
    credit_limit = int(credit_limit)
    result_filename_list[2] = 'ДС каталоги'

    word_path = os.path.join(solo_path, 'word_templates', filename)

    ###########################

    firm_name = '«' + firm_name.title() + '»'
    firm_type = firm_type.capitalize()
    full_firm_name = firm_type + ' ' + firm_name
    date_today = '«{:02d}» {} {} '.format(dt.now().day, mounth_names[dt.now().month], dt.now().year)
    if 'solo_decor' in word_path:
        date_today += 'г.'
    expire_date = '«{:02d}» {} {} года'.format(dt.now().day, mounth_names[dt.now().month], dt.now().year+3)

    position_1 = morph_word(position, {'sing', 'gent'}, its_name=False)
    if 'u_l' in word_path:
        director = morph_word(name, {'sing', 'gent'}, its_name=True)
    else:
        director = name
    # document = morph_word(document)

    director_short = ''
    for i, w in enumerate(name.split()):
        if i != 0:
            w = w[0] + '.'
        else:
            w = w + ' '
        director_short += w

    if credit_limit:
        credit_limit = '{} ({})'.format(credit_limit, morph_word(num2text(credit_limit), {'gent'}, its_name=False).rstrip())  ## добавить календарных дней
        if 'solo_decor_u' in word_path:
            credit_limit += ' календарных дней'
        elif 'solo_decor_ip' in word_path:
            credit_limit += ' календарных'
        elif 'alians' in word_path:
            pass

    if gender == 2:
        gender = 'именуемая'
    else:
        gender = 'именуемый'

    ############ work with word file ###############


    doc = DocxTemplate(word_path)

    context = {
        'date_today': date_today,
        'firm_name': firm_name,
        'director': director.title().rstrip(),
        'director_short': director_short.title(),
        'position_1': position_1.capitalize(),
        'position_2': position.capitalize(),
        'document': document.capitalize(),
        'credit_limit': credit_limit,
        'expire_date': expire_date,
        'ogrnip': ogrnip,
        'gender': gender,

    }
    doc.render(context)

    if firm_type == "Индивидуальный предприниматель":
        result_filename_list[1] = director_short

    result_filename = ' '.join(result_filename_list) + '.docx'
    save_path = os.path.join(solo_path, 'contracts', result_filename)
    doc.save(save_path)
    return result_filename, save_path

