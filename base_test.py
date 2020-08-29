
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from models import VCode, Consigment, Collection, base_path, Table_row
from openpyxl import load_workbook
import random, string, time
import os


def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def add_to_base():
    codes = ["E37108", 'E37100', 'E37105']

    for code in codes:
        code_in_base = session.query(VCode).filter(VCode.code == code).all()
        # print(code_in_base)
        if not code_in_base:
            session.add(VCode(code))

    for code in codes:
        code_in_base = session.query(VCode).filter(VCode.code == code).first()

        if random.randint(1, 3) == 2:
            name = random.randint(10358, 20067)
        else:
            name = randomword(4)

        consig = Consigment(name=name, vcode=code_in_base.id, amount=random.randint(6, 36))
        consig_in_base = session.query(Consigment).filter(
                                                    Consigment.vcode_id == code).filter(
                                                        Consigment.name == name).all()
        if not consig_in_base:
            session.add(consig)

    session.commit()

    for code in codes:
        code_in_base = session.query(VCode).filter(VCode.code == code).first()
        for consig in code_in_base.consigments:
            print(code_in_base.code, consig.name, consig.amount)


def read_xlxs(filepath):
    wb = load_workbook(filename=filepath)
    ws = wb[wb.sheetnames[0]]
    xlxs_rows = []
    for i, row in enumerate(ws.iter_rows()):
        if i == 0:
            continue
        vcode = row[0].value.split()[0]
        consig = row[1].value
        amount = row[2].value
        xlxs_rows.append((i, vcode, consig, amount))
    wb.close()
    return xlxs_rows


def get_all_from_base(xlxs_rows):
    codes = session.query(VCode).all()
    consigs = session.query(Consigment).all()

    need_commit = False
    for row in xlxs_rows:
        
        i = row[0]
        vcode = row[1]
        consig = row[2]
        amount = row[3]

        code_in_base = None
        for _code in codes:
            if _code.code == vcode:
                code_in_base = _code
                # codes.remove(_code)
                break
        if not code_in_base:
            session.add(VCode(vcode))
            session.commit()
            # need_commit = True
            code_in_base = session.query(VCode).filter(VCode.code == vcode).first()
            codes.append(code_in_base)

        consig_in_base = None
        for _consig in code_in_base.consigments:
            if _consig.name == consig:
                consig_in_base = _consig
                consigs.remove(_consig)
                break 
        if not consig_in_base:
            _consig = Consigment(name=consig, vcode=code_in_base.id, amount=amount)
            session.add(_consig)
            # session.commit()
            need_commit = True
            consig_in_base = session.query(Consigment).filter(
                                Consigment.vcode_id == code_in_base.id).filter(
                                    Consigment.name == consig).first()

        if amount != consig_in_base.amount:
            print('change {} amount from {} to {}'.format(consig_in_base.name, consig_in_base.amount, amount))
            consig_in_base.amount = amount
            need_commit = True

        if need_commit and not i % 100:
            session.commit()
            need_commit = False
        # if code_in_base.collection:
        #     print(i, code_in_base.collection.name, code_in_base.code, consig_in_base.name, consig_in_base.amount)
        #     print(consig_in_base.amount, amount)
        # else:
        #     print(i, "no collection", code_in_base.code, consig_in_base.name)


    print("rows_to_check: ", len(consigs))
    print("checked rows: ", i)
    for consig_in_base in consigs:
        # print('delete this consigments:')
        print('zero amount to this consigments')
        print(session.query(VCode).get(consig_in_base.vcode_id).code, consig_in_base.name)
        consig_in_base.amount = 0
        # session.delete(consig_in_base)
    session.commit()


def get_one_by_one():
    wb = load_workbook(filename=filepath)
    ws = wb[wb.sheetnames[0]]
    for i, row in enumerate(ws.iter_rows()):
        if i == 0:
            continue
        vcode = row[0].value
        consig = row[1].value
        amount = row[2].value

        code_in_base = session.query(VCode).filter(VCode.code == vcode).first()
        if not code_in_base:
            session.add(VCode(vcode))
            session.commit()
            code_in_base = session.query(VCode).filter(VCode.code == vcode).first()

        consig_in_base = session.query(Consigment).filter(
                            Consigment.vcode_id == code_in_base.id).filter(
                                Consigment.name == consig).first()
        if not consig_in_base:
            _consig = Consigment(name=consig, vcode=code_in_base.id, amount=amount)
            session.add(_consig)
            session.commit()
            consig_in_base = session.query(Consigment).filter(
                                Consigment.vcode_id == code_in_base.id).filter(
                                    Consigment.name == consig).first()

        if amount != consig_in_base.amount:
            consig_in_base.amount = amount
    wb.close()
    session.commit()


def add_boxes_to_vcodes():
    """Выгрузка из ABC"""
    codes = session.query(VCode).all()
    collections = session.query(Collection).all()

    wb = load_workbook(filename=filepath)
    ws = wb[wb.sheetnames[0]]

    need_commit = False
    for i, row in enumerate(ws.iter_rows()):
        if i < 6:
            continue
        vcode = row[0].value
        name = row[1].value
        collection = row[2].value
        box = row[3].value

        # print(i, vcode, collection, box)

        collection_in_base = None
        for _coll in collections:
            if _coll.name == collection:
                collection_in_base = _coll
                break
        if not collection_in_base:
            session.add(Collection(collection, box))
            session.commit()
            print("*" * 50, "commit", "*" * 50)
            collection_in_base = session.query(Collection).filter(Collection.name == collection).first()
            collections.append(collection_in_base)

        code_in_base = None
        for _code in codes:
            if _code.code == vcode:
                code_in_base = _code
                if not code_in_base.collection_id:
                    code_in_base.collection_id = collection_in_base.id
                    need_commit = True
                break
        if not code_in_base:
            print(i, vcode, collection, box)
            session.add(VCode(vcode, collection_in_base.id))
            need_commit = True
            # session.commit()
            # code_in_base = session.query(VCode).filter(VCode.code == vcode).first()
            # codes.append(code_in_base)

        if not i % 100 and need_commit:
            print("*" * 50, "commit", "*" * 50)
            session.commit()
            need_commit = False

    if need_commit:
        print("*" * 50, "commit", "*" * 50)
        session.commit()


def add_vcodes():
    codes = session.query(VCode).all()

    wb = load_workbook(filename=filepath)
    ws = wb[wb.sheetnames[0]]
    need_commit = False
    prev_vcode = ''
    for i, row in enumerate(ws.iter_rows()):
        if i == 0:
            continue
        vcode = row[0].value
        # consig = row[1].value
        # amount = row[2].value
        if vcode == prev_vcode:
            continue
        else:
            prev_vcode = vcode
        code_in_base = None
        for _code in codes:
            if _code.code == vcode:
                code_in_base = _code
                # codes.remove(_code)
                break
        if not code_in_base:
            session.add(VCode(vcode))
            # session.commit()
            need_commit = True
            print(i, 'added %s' % vcode)
            # code_in_base = session.query(VCode).filter(VCode.code == vcode).first()
            # codes.append(code_in_base)

        if need_commit and not i % 100:
            session.commit()
            need_commit = False

    wb.close()
    session.commit()


def get_for_table(data_str):
    data_list = data_str.split()

    # if len(data_list[1]) > 3:
    for_range = range(len(data_list))
    #     in_boxes = True
    # else:
    #     for_range = range(0, len(data_list), 2)
    #     in_boxes = False

    table_rows = []
    skip = False
    in_boxes = False
    boxes_num = 0
    for i in for_range:
        if skip:
            skip = False
            continue

        vcode = data_list[i]
        if i == for_range.stop-1 or len(data_list[i+1]) > 3:
            in_boxes = True
            # skip = True
        elif "*" in data_list[i+1]:
            in_boxes = True
            skip = True
            # boxes_num = int(data_list[i+1][1:])
            boxes_num = data_list[i+1].replace("*", "")
        else:
            in_boxes = False
            skip = True

        if not in_boxes:
            number = data_list[i + 1]
        else:
            number = 0

        # if len(vcode) < 4 and len(str(number)) > 3:
        #     vcode, number = number, vcode

        number = int(number)
        vcode = vcode.upper()
        row = Table_row(vcode, number)
        table_rows.append(row)

    # for row in table_rows:
        print('trying %s\n' % row.vcode)
        code_in_base = session.query(VCode).filter(VCode.code == row.vcode).first()
        _code_in_base = None
        if not code_in_base:
            row.comment += "арт. %s не найден " % row.vcode
            code_in_base = find_code(vcode, session)
            if not code_in_base:
                row.consig = ""
                # row.comment += "Артикул не найден "
                continue

            elif len(code_in_base) > 1:
                minimal = min([code.code for code in code_in_base], key=len) # самый короткий артикул
                row.comment += "Возможные артикулы: "
                for _code in code_in_base:
                    row.comment += _code.code + " "
                    if _code.code == minimal:
                        _code_in_base = _code   # выбор самого короткого артикула
                    # row.vcode = code_in_base[0].code
                    continue
            else:
                # row.comment += "Возможно нужен %s " % code_in_base[0].code
                row.vcode = code_in_base[0].code
                code_in_base = code_in_base[0]
            # continue
        if _code_in_base:
            code_in_base = _code_in_base
            row.vcode = code_in_base.code

        if in_boxes:
            if code_in_base.collection:
                if boxes_num:
                    row.number = code_in_base.collection.boxes * int(boxes_num)
                    boxes_num = 0
                else:
                    row.number = code_in_base.collection.boxes
            else:
                row.number = 1
        if code_in_base.consigments:
            enough = False
            for consig in code_in_base.consigments:
                print("*"*10, '\n', locals(), '\n', "*"*20)
                print("*"*10, '\n',row.vcode, row.consig, row.number, '\n', "*"*20)
                if consig.amount >= row.number:
                    enough = True
                    if consig.name:
                        row.consig = consig.name
                    break
            if not enough:
                row.comment += "Недостаточно на св. остатке."
                add_comment = " в наличии есть партии: "
                max_num_consig = None
                max_num = 0
                for consig in code_in_base.consigments:
                    if consig.amount >= 0:
                        if consig.amount > max_num:
                            max_num_consig = consig.name
                            max_num = consig.amount
                        add_comment += "{} {} рул. ".format(consig.name, consig.amount)
                row.consig = max_num_consig
                if len(add_comment) > 24:
                    row.comment += add_comment
        else:
            row.consig = "Общая"
            row.comment = "Партий не найдено"
    return table_rows


def find_code(vcode, session):
    # code_in_base = session.query(VCode).filter(vcode in VCode.code).first()
    code_in_base = session.query(VCode).filter(VCode.code.contains(vcode)).all()

    if not code_in_base:
        return False
    len_vcode = len(vcode)
    # print('len_vcode', len_vcode)
    for i, code in enumerate(code_in_base.copy()):
        # print(len(code.code))
        if len(code.code) > len_vcode+2:
            code_in_base.remove(code)

    # if len(code_in_base) > 1:
    #     return min([code.code for code in code_in_base], key=len)

    return code_in_base


def find_analog_photowp(vcode, session):
    digit_code = ""
    for lett in vcode:
        if lett.isdigit():
            digit_code += lett
        else:
            break
    response = find_code(digit_code, session)
    codes = []
    for _code in response.copy():
        if "V" in _code.code or "P" in _code.code:
            if len(_code.consigments) > 0 and _code.consigments[0].amount > 0:
                codes.append(_code)
    return codes


def find_duplicates():
    codes = session.query(VCode).all()
    deleted_id = []
    # print(len(codes), len(codes.copy()))
    for code in codes.copy():
        # print("checking %s" % code.code)
        code_in_base = session.query(VCode).filter(VCode.code.contains(code.code)).all()

        if len(code_in_base) > 1:
            # print(code_in_base)
            for c in code_in_base:
                if c.id == code.id:
                    continue
                if c.code.split()[0] == code.code.split()[0]:
                    print(c.id, c.code)
                    print(code.id, code.code)
                    # print("id %d code %s" % (c.id, c.code))
                    print("consigments %s" % c.consigments)
                    if c.id > code.id:
                        for consig in c.consigments:
                            consig.vcode_id = code.id
                            session.commit()
                        session.delete(c)
                        session.commit()
                        print("deleted")


if __name__ == '__main__':
    # base_filename = "base_test.bd"
    # base_path = os.path.join(os.getcwd(), base_filename)
    # base_path = r'/home/django/bike_shop/solo/base_test.bd'
    # filepath = r'/home/django/bike_shop/solo/base.xlsx'
    filepath = os.path.join(os.getcwd(), "base.xlsx")

    engine = create_engine('sqlite:///%s' % base_path, echo=False, poolclass=QueuePool)
    Session = sessionmaker(bind=engine)
    session = Session()

    # start = time.time()
    # get_one_by_one()
    # end = time.time()
    # print("get_one_by_one done in {} sec".format(end-start))

    # start = time.time()
    # xlxs_rows = read_xlxs(filepath)
    # get_all_from_base(xlxs_rows)
    # end = time.time()
    # print("get_all_from_base done in {} sec".format(end-start))

    # add_to_base()

    # add_vcodes()

    filepath = r'/home/django/bike_shop/solo/abc.xlsx'
    add_boxes_to_vcodes()

    # filepath = r'/home/django/bike_shop/solo/base.xlsx'
    # add_vcodes()

    # request_str = "EL21201 2 e37105 *2 N55664 4 167062-90 894P8 136P8"
    # request_str = "21201 37108 *20 55664 167062-90 894p8 136p4"
    # response = get_for_table(request_str)
    # for row in response:
    #     print(row.vcode, row.consig, row.number, row.comment)

    # print(session.query(Collection).get(75).vcodes[0].code)

    # request_str = "21201 37105 55664 167062-90 894p8 136p4"
    # for code in request_str.split():
    #     resp = find_code(code, session)
    #     # print(resp)
    #     print(code)
    #     for r in resp:
    #         print(r.code, r.id, [c.name for c in r.consigments])
    #         print()

    # find_duplicates()

    # request_str = '37108'
    # cc = find_code(request_str, session)
    # for code in cc:
    #     print(code.id, code.code)
    #     for consig in code.consigments:
    #         print(consig.id, consig.name , consig.amount, consig.vendor_code.code)



    # print("*"*50)
    # wb = load_workbook(filename=filepath)
    # ws = wb[wb.sheetnames[0]]

    # last_r = None
    # new_r = None
    # for i, row in enumerate(ws.iter_rows()):
    #     # if i == 2281:
    #     # if i in [2281, 2280, 2279]:
    #     if row[0].value.split()[0] == "E37108":
    #         for r in row:
    #             print(r.value)
    #         # break
    # wb.close()


    # consigs = session.query(Consigment).all()
    # consig_in_base = None
    # for _consig in consigs:
    #     if _consig.name == '012' and _consig.amount == 9:
    #         print(_consig.id , _consig.vendor_code.code)

    session.close()
