# Purpose: Define util functions for the project
# Author: ABHISHEK GUPTA <abhishek@quantgrade.com>

import numpy as np
import pandas as pd
import yaml
from datetime import datetime, timedelta
from src import *


def download_gsheet(gspread_client, config, dataPath):
    workbook = gspread_client.open_by_key(config['spreadsheet_id'])
    worksheet = workbook.worksheet(config['worksheet_name'])

    data = worksheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)

    df.replace('\$', '', regex=True, inplace=True)
    df.replace('\,', '', regex=True, inplace=True)
    return df


def create_pine_script(df):
    pine_script = []
    pine_script.append(
        '// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/')
    pine_script.append('// © deerfieldgreen')
    pine_script.append('')
    pine_script.append('//@version=5')
    pine_script.append('indicator("Daily Range Levels", overlay=true)')
    pine_script.append('')

    colors = {'upper_value': '#eb8704', 'lower_value': '#eb8704', 'PLower2': 'color.purple', 'PLower1': 'color.purple',
              'PMean': 'color.purple', 'PUpper1': 'color.purple', 'PUpper2': 'color.purple'}
    for level, color in colors.items():
        pine_script.append(f'var float y_{level} = na')

    pine_script.append('')
    for index, row in df.iterrows():
        symbol = row['ticker']
        pine_script.append(f'// Symbol: {symbol}')
        pine_script.append(f'if syminfo.ticker == "{symbol}"')
        for level, color in colors.items():
            y_level = row[level]
            label_color = color if color == '#eb8704' else 'color.rgb(208, 154, 218)'
            xloc = 'last_bar_index' if level not in ['upper_value', 'lower_value'] else 'last_bar_index-1'
            pine_script.append(f'    var label lbl_{level} = na')
            pine_script.append(f'    label.delete(lbl_{level})')
            pine_script.append(f'    y_{level} := {y_level}')
            pine_script.append(
                f'    line.new(x1=bar_index, y1=y_{level}, x2=bar_index+1, y2=y_{level}, color={color}, width = 2, extend = extend.both)')
            pine_script.append(
                f'    lbl_{level} := label.new({xloc}, y_{level}, text="{level}", textcolor={color}, style=label.style_none, size=size.small)')
            pine_script.append('')

        # Note with SMA details
        anchoredBarIndex = 10  # Replace this with the specific bar index you want
        anchoredPriceLevel = round(row['PUpper2'] * 1.005, 2)  # Replace this with the specific price level you want
        note = (f"SMA10 - {round(row['straddle_pct_sma10']*100,3)}%\\n"
                f"SMA20 - {round(row['straddle_pct_sma20']*100,3)}%\\n"
                f"SMA30 - {round(row['straddle_pct_sma30']*100,3)}%\\n"
                f"SMA50 - {round(row['straddle_pct_sma50']*100,3)}%\\n\\n"
                f"IV Rank - {round(row['implied_vol_rank']*100,3)}%\\n"
                f"IV Percent - {round(row['implied_vol_percentile']*100,3)}%")

        pine_script.append(f'    var int anchoredBarIndex = {anchoredBarIndex}')
        pine_script.append(f'    var float anchoredPriceLevel = {anchoredPriceLevel}')
        pine_script.append('')
        pine_script.append(f'    var label myLabel = na')
        pine_script.append(f'    var string note = "{note}"')
        pine_script.append('')
        pine_script.append(f'    if (bar_index == anchoredBarIndex)')
        pine_script.append(
            '        myLabel := label.new(x=bar_index, y=anchoredPriceLevel, text=note, style=label.style_label_down, color=#fffc684a, textcolor=#fffffff1, yloc=yloc.price)')
##      myLabel := label.new(x=bar_index, y=anchoredPriceLevel, text=note, style=label.style_label_down, color=color.rgb(255, 252, 104, 71), textcolor=#fffffff1, yloc=yloc.price)
##  myLabel := label.new(x=bar_index, y=anchoredPriceLevel, text=note, style=label.style_label_down, color=color.rgb(232, 210, 10), textcolor=color.white, yloc=yloc.price)')
##  color=#6888ff4a, textcolor=#fffffff1
        pine_script.append('')
        pine_script.append('    if not na(myLabel)')
        pine_script.append('        label.set_xy(id=myLabel, x=bar_index, y=anchoredPriceLevel)')
        pine_script.append('        label.set_text(id=myLabel, text=note)')
        pine_script.append('')

    combined = '\n'.join(pine_script)

    # Save to notepad file
    with open('daily_range_pine.txt', 'w') as file:
        file.write(combined)

    return combined


if __name__ == '__main__':
    df = download_gsheet()
    pine_script = create_pine_script(df)
    print(pine_script)
