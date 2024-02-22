import datetime
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
pd.set_option('display.max_columns', None) # to ensure console display all columns
pd.set_option('display.float_format', '{:0.3f}'.format)
pd.set_option('display.max_row', 50)

import os
from pathlib import Path
from src.utils import (
    load_config,
)
import gspread
from pathlib import Path
from src.utils import (
    download_gsheet, create_pine_script
)
from github import Github
import configparser

def get_token(config):
    token = config['SETUP']['GIT_TOKEN']
    return token

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('config.ini')

    root_folder = "."
    projectPath = Path(rf'{root_folder}')

    dataPath = projectPath / 'data'
    pickleDataPath = dataPath / 'pickle'
    dataInputPath = dataPath / 'input'
    configPath = projectPath / 'config'
    credsPath = projectPath / 'credentials'

    ##############################################################################
    ## Settings

    settings_config = load_config(path=configPath / "settings.yml")

    token = get_token(config)
    g = Github(token)
    repo = g.get_repo("deerfieldgreen/daily-levels-painting")  # Replace with your repo details
    file = repo.get_contents("daily_range_pine.txt")  # Path to your file in the repository

    gspread_client = gspread.service_account(credsPath / 'gsheet' / "creds.json")

    df = download_gsheet(gspread_client, settings_config, dataPath)
    print("Downloaded gsheet")

    pine_script = create_pine_script(df)
    print(pine_script)

    # push to github
    if config['SETUP']['WRITE'] == 'Y':
        repo.update_file(file.path, f"Updated file for {datetime.datetime.today().date()}", pine_script, file.sha)
        print("Pushed to github")
    else:
        print("Not pushed to github")


