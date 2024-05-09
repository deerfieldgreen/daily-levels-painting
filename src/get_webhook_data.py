# Author: ABHISHEK GUPTA <abhishek@quantgrade.com>

# Purpose: Retrieve data from webhook


import numpy as np
import pandas as pd
import os
import sys
import time
from tenacity import retry, stop_after_attempt, wait_random_exponential
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from datetime import datetime, timedelta
import datetime as dt
from typing import Optional
import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None) # to ensure console display all columns
pd.set_option('display.float_format', '{:0.3f}'.format)
pd.set_option('display.max_row', 50)
from pathlib import Path
import joblib
from copy import deepcopy
from src.update_pine import *

root_folder = "."
projectPath = Path(rf'{root_folder}')

dataPath = projectPath / 'data'
pickleDataPath = dataPath / 'pickle'
dataInputPath = dataPath / 'input'
configPath = projectPath / 'config'
credsPath = projectPath / 'credentials'

import pickle
def save_obj(obj, name):
    with open(pickleDataPath / f'{name}.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(pickleDataPath / f'{name}.pkl', 'rb') as f:
        return pickle.load(f)


##############################################################################
## Imports

from src.utils import (
    load_config,
)

import gspread
from gspread_dataframe import set_with_dataframe


##############################################################################
## Settings

settings_config = load_config(path=configPath / "settings.yml")
flask_settings = load_config(path=configPath / "flask.yml")


##############################################################################
## Initialize

app = FastAPI(title="QC EndPoint V3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sys.stdout.flush()


global data_df
data_df = pd.DataFrame()


##############################################################################
## Definitions

class InputRequest(BaseModel):
    auth: str
    prediction_output_list: list


######################################################
## Variables
config = configparser.ConfigParser()
config.read('config.ini')

token = get_token(config)
g = Github(token)
repo = g.get_repo("deerfieldgreen/daily-levels-painting")  # Replace with your repo details
file = repo.get_contents("daily_range_pine.txt")  # Path to your file in the repository


##############################################################################
## Functions

@app.get("/")
async def root():
    return "I am alive!"


@app.post("/test")
async def test_api():
    return {"text": "test"}


# @app.post("/webhook")
# async def webhook(r: InputRequest):
#
#     auth = r.auth
#     prediction_output_list = r.prediction_output_list
#     if auth != flask_settings["auth"]:
#         print(f"Invalid Authentication")
#         return {"message": "ERROR: Unauthorized"}, 401
#
#     data_df = pd.DataFrame(prediction_output_list)
#     data_df = data_df[config['col_prediction']]
#     workbook = gspread_client.open_by_key(config['spreadsheet_id'])
#     worksheet = workbook.worksheet(config['worksheet_name'])
#     worksheet.clear()
#     set_with_dataframe(
#         worksheet=worksheet, dataframe=data_df, include_index=False,
#         include_column_header=True, resize=True,
#     )
#     print(f"# {datetime.utcnow()}: {config['worksheet_name']}: Spreadsheet Updated")
#     print(data_df)
#     sys.stdout.flush()
#
#     return {"success": True}, 200

@app.post("/webhook")
async def webhook(r: InputRequest):
    global data_df
    auth = r.auth
    prediction_output_list = r.prediction_output_list
    if auth != flask_settings["auth"]:
        print(f"Invalid Authentication")
        return {"message": "ERROR: Unauthorized"}, 401

    data_df_update = pd.DataFrame(prediction_output_list)
    data_df_update = data_df_update[settings_config['col_prediction']]
    data_df = pd.concat([data_df, data_df_update])
    data_df.reset_index(drop=True, inplace=True)
    date_max = pd.to_datetime(data_df['datetime']).dt.date.max()
    idx = pd.to_datetime(data_df['datetime']).dt.date == date_max
    data_df = data_df[idx]
    data_df.reset_index(drop=True, inplace=True)
    data_df.drop_duplicates('ticker', keep='first', inplace=True)
    data_df.reset_index(drop=True, inplace=True)
    counter = 1
    has_updated_github = False
    while not has_updated_github:
        try:
            pine_script = create_pine_script(data_df)
            print(pine_script)
            print(file)
            if config['SETUP']['WRITE'] == 'Y':
                repo.update_file(file.path, f"Updated file for {datetime.datetime.today().date()}", pine_script,
                                 file.sha)
            else:
                # Save text file locally
                with open('daily_range_pine_local.txt', 'w') as f:
                    f.write(pine_script)

            has_updated_github = True
        except:
            print(f"# {dt.datetime.utcnow()}: Failed Pine Update Attempt {counter}")
            counter += 1
            time.sleep(30)
        if counter > 3:
            break
    if has_updated_github:
        print(f"# {dt.datetime.utcnow()}: Pine Updated on Github")
        print(data_df)
    else:
        print(f"# {dt.datetime.utcnow()}: Failed to update Pine on Github !!")
    sys.stdout.flush()

    return {"success": True}, 200