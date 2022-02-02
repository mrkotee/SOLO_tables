
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sng_models import base_path, VCode, Client, CodeName
from sng_funcs import read_xlxs, add_names_to_base, change_names




ex_code = '0518v8'
ex_code_name = 'fotowall 0518v8 lorem ipsum'
ex_code_name_2 = 'fotowall 0518v8 sookai'
client_name = 'High less'
client_name_2 = 'High more'


def first_step():
    try:
        session.add(VCode(ex_code))
        session.commit()

        base_code = session.query(VCode).filter(VCode.code == ex_code).first()
        session.add(CodeName(ex_code_name, base_code.id))
        session.commit()

        session.add(Client(client_name))
        session.commit()
    except:
        session.rollback()

    client = session.query(Client).first()
    code_name = session.query(CodeName).first()

    code_name.clients.append(client)

    print(code_name.clients[0].name)
    print(client.code_names[0].name)


# try:
#     base_code = session.query(VCode).filter(VCode.code == ex_code).first()
#     session.add(CodeName(ex_code_name_2, base_code.id))
#     session.commit()
#
#     session.add(Client(client_name_2))
#     session.commit()
# except:
#     session.rollback()

# client = session.query(Client).filter(Client.name == client_name_2).first()
# code_name = session.query(CodeName).filter(CodeName.name == ex_code_name_2).first()
#
# code_name.clients.append(client)
# session.commit()


if __name__ == "__main__":
    engine = create_engine('sqlite:///%s' % base_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # first_step()

    filename = 'spec.xlsx'
    # filename = 'УПД.xlsx'
    filename = 'ТОРГ-12_sng.xlsx'
    filepath = os.path.join(os.getcwd(), filename)
    #
    # codes_dict = read_xlxs(filepath)

    # add_names_to_base(session, codes_dict)
    # add_names_to_base(session, codes_dict, client_name)

    # for client in session.query(Client).all():
    #     print(client.name)
    #     for code_name in client.code_names:
    #         print(code_name.vendor_code.code, code_name.name)

    # for code_name in session.query(CodeName).all():
    #     if not "E3" in code_name.name:
    #         continue
    #     print(code_name.vendor_code.code)
    #     for client in code_name.clients:
    #         print(client.name, '  ', code_name.name)

    new_path = 'newupd.xlsx'
    change_names_xlxs(session, filepath, new_path, client_name)

    session.close()
