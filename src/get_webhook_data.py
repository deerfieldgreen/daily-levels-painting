# Purpose: Retrieve data from webhook
# Author: ABHISHEK GUPTA <abhishek@quantgrade.com>

import os
import pandas as pd
from github import Github
import sys
import time
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from datetime import datetime
import datetime as dt
import warnings
import io

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", None)  # to ensure console display all columns
pd.set_option("display.float_format", "{:0.3f}".format)
pd.set_option("display.max_row", 50)
from pathlib import Path
import joblib
from copy import deepcopy
from src import *

root_folder = "."
debug = True if os.environ.get("debug") != "False" else False
projectPath = Path(rf"{root_folder}")

dataPath = projectPath / "data"
pickleDataPath = dataPath / "pickle"
dataInputPath = dataPath / "input"
credsPath = projectPath / "credentials"

##############################################################################
## Initialize

app = FastAPI(title="QC EndPoint V3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:8080",
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

token = os.environ.get("GIT_TOKEN")
if not token:
    try:
        secret_id = "Daily_Range_GITHUB_TOKEN"
        project_id = "367674009031"
        token = access_secret_version(project_id, secret_id)
        print(f"# {dt.datetime.utcnow()}: Successfully retrieved GitHub token from Secret Manager")
    except Exception as e:
        print(f"# {dt.datetime.utcnow()}: Error retrieving GitHub token from Secret Manager: {e}")
        token = None

g = Github(token)
repo = g.get_repo(
    "deerfieldgreen/daily-levels-painting"
)  # Replace with your repo details

col_prediction = [
    "ticker",
    "datetime",
    "spot_price",
    "upper_value",
    "lower_value",
    "straddle_value",
    "past_straddle_value",
    "straddle_pct_value",
    "past_straddle_pct_value",
    "PLower3",
    "PLower2",
    "PLower1",
    "PMean",
    "PUpper1",
    "PUpper2",
    "PUpper3",
    "straddle_pct_sma10",
    "straddle_pct_sma20",
    "straddle_pct_sma30",
    "straddle_pct_sma50",
    "implied_vol_rank",
    "implied_vol_percentile"
]


##############################################################################
## Functions


@app.get("/")
async def root():
    return "I am alive!"


@app.post("/test")
async def test_api():
    return {"text": "test"}


@app.post("/webhook")
async def webhook(r: InputRequest):
    file = (
        repo.get_contents("daily_range_pine.txt")
        if not debug
        else repo.get_contents("test_pine.txt")
    )  # Path to your file in the repository

    global data_df
    auth = r.auth
    prediction_output_list = r.prediction_output_list
    if auth != os.environ["flask_auth"]:
        print(f"Invalid Authentication")
        return {"message": "ERROR: Unauthorized"}, 401

    data_df_update = pd.DataFrame(prediction_output_list)
    data_df_update = data_df_update[col_prediction]
    # data_df = pd.concat([data_df, data_df_update])
    data_df = data_df_update
    data_df.reset_index(drop=True, inplace=True)
    date_max = pd.to_datetime(data_df["datetime"]).dt.date.max()
    idx = pd.to_datetime(data_df["datetime"]).dt.date == date_max
    data_df = data_df[idx]
    data_df.reset_index(drop=True, inplace=True)
    data_df.drop_duplicates("ticker", keep="first", inplace=True)
    data_df.reset_index(drop=True, inplace=True)
    counter = 1
    has_updated_github = False
    while not has_updated_github:
        try:
            pine_script = create_pine_script(data_df)

            repo.update_file(
                file.path,
                f"Updated daily_range_pine.txt for {datetime.today().date()}",
                pine_script,
                file.sha,
            )

            has_updated_github = True
        except Exception as e:
            print(e)
            print(f"# {dt.datetime.utcnow()}: Failed Pine Update Attempt {counter}")
            counter += 1
            time.sleep(30)
        if counter > 3:
            break
    
    # Create and upload CSV file to GitHub
    current_date = datetime.today().date().strftime("%Y-%m-%d")
    csv_filename = f"data_{current_date}.csv"
    csv_path = f"data/{csv_filename}"
    
    counter = 1
    has_updated_csv = False
    while not has_updated_csv and counter <= 3:
        try:
            # Convert DataFrame to CSV string
            csv_buffer = io.StringIO()
            data_df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            # Check if file already exists in repo
            try:
                csv_file = repo.get_contents(csv_path)
                # File exists, update it
                repo.update_file(
                    csv_path,
                    f"Updated {csv_filename} for {current_date}",
                    csv_content,
                    csv_file.sha,
                )
            except Exception:
                # File doesn't exist, create it
                repo.create_file(
                    csv_path,
                    f"Created {csv_filename} for {current_date}",
                    csv_content,
                )
            
            has_updated_csv = True
            print(f"# {dt.datetime.utcnow()}: CSV file {csv_filename} uploaded to GitHub")
        except Exception as e:
            print(e)
            print(f"# {dt.datetime.utcnow()}: Failed CSV Update Attempt {counter}")
            counter += 1
            time.sleep(30)
    
    if has_updated_github:
        print(f"# {dt.datetime.utcnow()}: Pine Updated on Github")
        print(data_df)
    else:
        print(f"# {dt.datetime.utcnow()}: Failed to update Pine on Github !!")
    
    if not has_updated_csv:
        print(f"# {dt.datetime.utcnow()}: Failed to upload CSV to Github !!")
    
    sys.stdout.flush()

    return {"success": True}, 200