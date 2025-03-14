import os
from uuid import uuid4
from datetime import datetime
from typing import List

import pandas as pd
from loguru import logger
from fastapi import UploadFile
from pandas import DataFrame


def check_file_type(file: UploadFile):
    file_ext = file.filename.rsplit('.', 1)[-1]
    if not file.filename.endswith(('.zip', '.rar', '.csv')):
        raise Exception("Incorrect file type")
    match file_ext:
        case "csv":
            return 1
        case "zip" | 'rar':
            return 2
        case _:
            return 3


def convert_date(date: str) -> datetime:
    return datetime.strptime(date, '%d-%b-%y %H:%M:%S.%f')


def convert_csv_to_dataframe(
        storage: str,
        header_list: List[str],
        object_id: int
) -> List[DataFrame]:
    logger.info('Start converting csvs to dataframe')
    tmp_storage = os.walk(storage)
    df_list = []
    for root, _, files in tmp_storage:
        for file in files:
            data = pd.read_csv(
                os.path.join(root, file),
                names=header_list, delimiter=',',
                engine='python'
            )
            data[str(object_id)] = uuid4()
            data['indicator'] = pd.to_numeric(data['indicator'], errors='coerce')
            data['date'] = data['date'].apply(convert_date)
            data['indicator'] = data['indicator'].astype('float64')
            df_list.append(data)
    logger.success('Finished converting csvs to dataframe')
    return df_list
