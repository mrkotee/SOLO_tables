import os


solo_path = r'C:\Users\User\PycharmProjects\bike_shop\solo'

xlxs_filepath = os.path.join(solo_path, r'base.xlsx')

xlxs_abc_filepath = os.path.join(solo_path, r'abc.xlsx')

base_path = os.path.join(solo_path, r'base.bd')

name_base_path = os.path.join(solo_path, r'name_base.bd')

mail_set_base_path = os.path.join(solo_path, r'mail_base.bd')

statistics_base_path = os.path.join(solo_path, r'statistics_base.bd')

sng_base_path = os.path.join(solo_path, r'sng_base.bd')

docs_temp_dir = os.path.join(solo_path, r'docs_temp/')

sep_files_dir = os.path.join(solo_path, r'separated_by_factories/')

exclusive_collections = ['roberto', 'valentin', 'ferre']


replace_dict = {
    'Е': 'E',
    'Р': 'P',
    'А': 'A',
    'К': 'K',

}  # key - letter in russian, value - letter in english


mounth_names = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
                5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
                9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}

