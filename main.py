from json import dumps
from json import load
from logging import INFO
from logging import basicConfig
from logging import getLogger

from arrow import now
from pandas import DataFrame
from pandas import read_excel


def get_excel_data(sheet_name, url: str) -> DataFrame:
    result_df = read_excel(io=url, sheet_name=sheet_name, )
    return result_df


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

    df = get_excel_data(sheet_name=settings['dewey_sheet_name'], url=settings['dewey_url'], )
    logger.info(msg=df.shape)
    df = df[df['Summary'] == 3].drop(columns=['Summary'])
    df = df[df['Caption'] != '[Unassigned]']

    DEBUG['data'] = df

    time_seconds = (now() - time_start).total_seconds()
    logger.info(msg='done: {:02d}:{:05.2f}'.format(int(time_seconds // 60), time_seconds % 60, ))


DEBUG = {}
OUTPUT_FOLDER = './result/'
USECOLS = []

if __name__ == '__main__':
    main()
