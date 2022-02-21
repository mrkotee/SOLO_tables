
import unittest
import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
# from openpyxl import load_workbook
from alchemy_models import base_path, VCode, Consigment, Collection, Table_row, path_for_old_base
from funcs import get_for_table
from solo_settings import xlxs_filepath, xlxs_abc_filepath, docs_temp_dir


class TableTestCase(unittest.TestCase):
    """Test for 'funcs.py'."""

    def setUp(self):

        engine = create_engine('sqlite:///%s' % base_path, echo=False)
        Session = sessionmaker(bind=engine)
        self.table_session = Session()
        

    def test_separate_string_vcodes(self):

        request_str = "rmg 2301-1 2303-1 2050"

        table_rows = get_for_table(request_str.split(), self.table_session)

        self.assertEqual(table_rows[0].vcode, 'RMG2301-1')
        self.assertEqual(table_rows[1].vcode, 'RMG2303-1')
        self.assertEqual(table_rows[2].vcode, 'AK2050')


    def test_nonexistent_vcodes(self):

        request_str = "ak 20115 240222"

        table_rows = get_for_table(request_str.split(), self.table_session)

        self.assertEqual(table_rows[0].comment, 'Артикул не найден ')
        self.assertEqual(table_rows[1].comment, 'Артикул не найден ')


    def test_boxes(self):

        request_str = "e37105 *2"

        table_rows = get_for_table(request_str.split(), self.table_session)

        self.assertEqual(table_rows[0].number, 12)

        request_str = "240509 240461"

        table_rows = get_for_table(request_str.split(), self.table_session, all_boxes_num=2)

        self.assertEqual(table_rows[0].number, 12)
        self.assertEqual(table_rows[1].number, 12)


    def test_get_all_consigs(self):
        codes = self.table_session.query(VCode).all()
        number = 0
        for code in codes:
            if len(code.consigments) > 2:
                number = sum([consig.amount for consig in code.consigments]) + random.randint(3, 20)
                break

        request_str = '%s %d' % (code.code, number)

        table_rows = get_for_table(request_str.split(), self.table_session, get_all_consigs=True)

        t_r_consigs = [r.consig for r in table_rows]
        for consig in code.consigments: 
            self.assertIn(consig.name, t_r_consigs)
        self.assertEqual(number, sum([r.number for r in table_rows]))


    def test_get_all_consigs_boxes(self):
        codes = self.table_session.query(VCode).all()
        number_boxes = 0
        for code in codes:
            enough_consigs = 0
            rolls_in_box = code.collection.boxes
            if len(code.consigments) > 2:
                for consig in code.consigments:
                    if consig.amount > rolls_in_box:
                        enough_consigs += 1
                if enough_consigs > 2:
                    number_boxes = sum([consig.amount for consig in code.consigments]) // rolls_in_box + random.randint(3, 5)
                    break

        request_str = '%s *%d' % (code.code, number_boxes)

        table_rows = get_for_table(request_str.split(), self.table_session, get_all_consigs=True)

        t_r_consigs = [r.consig for r in table_rows]
        for consig in code.consigments: 
            self.assertIn(consig.name, t_r_consigs)
        self.assertEqual(number_boxes, sum([r.number for r in table_rows])/rolls_in_box)


unittest.main()

