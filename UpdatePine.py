import warnings
warnings.filterwarnings('ignore')

import pandas as pd
pd.set_option('display.max_columns', None) # to ensure console display all columns
pd.set_option('display.float_format', '{:0.3f}'.format)
pd.set_option('display.max_row', 50)

from pathlib import Path
from src.utils import (
    load_config,
)
import gspread
from pathlib import Path
from src.utils import (
    download_gsheet, create_pine_script
)

if __name__ == "__main__":

    root_folder = "."
    projectPath = Path(rf'{root_folder}')

    dataPath = projectPath / 'data'
    pickleDataPath = dataPath / 'pickle'
    dataInputPath = dataPath / 'input'
    configPath = projectPath / 'config'
    credsPath = projectPath / 'credentials'

    ##############################################################################
    ## Settings

    config = load_config(path=configPath / "settings.yml")
    gspread_client = gspread.service_account(credsPath / 'gsheet' / "creds.json")

    df = download_gsheet(gspread_client, config, dataPath)
    print("Downloaded gsheet")

    pine_script = create_pine_script(df)
    print(pine_script)

