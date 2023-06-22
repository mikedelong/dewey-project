from json import dumps
from json import load
from logging import INFO
from logging import basicConfig
from logging import getLogger

from arrow import now
from pandas import DataFrame
from pandas import concat
from pandas import read_excel


def get_baseline_data(sheet_name, url: str) -> DataFrame:
    result_df = read_excel(io=url, sheet_name=sheet_name, dtype={'Class': str}, )
    return result_df


def get_books_data(filename: str) -> DataFrame:
    return concat(
        [read_excel(dtype={'Dewey': str}, engine='openpyxl', io=filename, sheet_name=str(year) + ' Counts',
                    usecols=('Date', 'Dewey', 'Author', 'Title',), )
         for year in range(2017, 2024)])


def load_settings(filename: str, ) -> dict:
    with open(encoding='utf-8', file=filename, mode='r') as input_fp:
        result = dict(load(fp=input_fp, ))
    return {key: value for key, value in result.items() if key in result['keys']}


def main():
    time_start = now()
    basicConfig(level=INFO, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s', )
    logger = getLogger(name='main', )
    settings = load_settings(filename='main.json', )
    logger.info(msg='settings: {}'.format(dumps(indent=4, obj=settings, sort_keys=True, ), ), )

    df = get_baseline_data(sheet_name=settings['dewey_sheet_name'], url=settings['dewey_url'], )
    logger.info(msg=df.shape)
    df = df[df['Summary'] == 3].drop(columns=['Summary'])
    df = df[df['Caption'] != '[Unassigned]']
    languages_df = df[df['Caption'].apply(lambda x: any([y in str(x) for y in LANGUAGES]) and 'islands' not in x)]

    read_df = get_books_data(filename=DATA_FOLDER + settings['books_read_file'])
    read_df = read_df[~read_df['Dewey'].isna()]
    read_df['Class'] = read_df['Dewey'].apply(func=lambda x: str(x).split('.')[0])
    read_df = read_df.sort_values(by=['Class', 'Date'])
    DEBUG['read'] = read_df
    logger.info(read_df.shape)
    short_df = read_df.groupby(by='Class').first()

    # merge out the language classes
    remaining_df = df.merge(right=languages_df, how='outer', on='Class', indicator=True)
    remaining_df = remaining_df[remaining_df['_merge'] == 'left_only'].drop(columns=['Caption_y', '_merge']).rename(
        columns={'Caption_x': 'Caption'})

    # merge out the read books
    remaining_df = remaining_df.merge(right=short_df, how='outer', on='Class', indicator=True)

    todo_df = remaining_df[remaining_df['_merge'] == 'left_only'].drop(columns=['_merge', 'Date', 'Dewey', 'Title',
                                                                                'Author'])
    DEBUG['data'] = df
    DEBUG['languages'] = languages_df
    DEBUG['remaining'] = remaining_df
    DEBUG['short'] = short_df
    DEBUG['todo'] = todo_df

    time_seconds = (now() - time_start).total_seconds()
    logger.info(msg='done: {:02d}:{:05.2f}'.format(int(time_seconds // 60), time_seconds % 60, ))


DATA_FOLDER = './data/'
DEBUG = {}
LANGUAGES = ['Catalan', 'French', 'Germanic', 'Italian', 'Occitan', 'Portuguese', 'Romanian', 'Scandinavian', 'Slavic',
             'Spanish']
OUTPUT_FOLDER = './result/'

if __name__ == '__main__':
    main()
