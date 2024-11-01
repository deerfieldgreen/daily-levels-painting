#region imports
from AlgorithmImports import *
#endregion


## General Settings
general_setting = {
   "tickers": {
        "QQQ": {"type": "equity"},
        "SPY": {"type": "equity"},
        "SPX": {"type": "equity"},
        "NVDA": {"type": "equity"},
        "TSLA": {"type": "equity"},
        "BABA": {"type": "equity"},
        "META": {"type": "equity"},
        "AMZN": {"type": "equity"},
        "TLT": {"type": "equity"},
        "GLD": {"type": "equity"},
        "SLV": {"type": "equity"},
        "EWZ": {"type": "equity"},
        "IWM": {"type": "equity"}
    },


#2024.05.20 - New Deploy
# Base URL - https://daily-levels-painting-fvnqwgrq6q-uc.a.run.app
# dailyrange.deerfieldgreen.com = CNAME in GoDaddy DNS - kevin.stoll@deerfieldgreen.com
   "url": "https://dailyrange.deerfieldgreen.com/webhook",
   "auth": "siycfsYts$dr7kv135bd&",


    "model_name": "DAILYRANGE_V3_15",
    "use_init_data": False,
    "model_name_init": "DAILYRANGE_V3_15",
    "ref_ticker": "QQQ",
    "ref_hour": 9,
    "ref_minute": 39,
    "quantile_list": [0.01, 0.025, 0.05, 0.10, 0.25, 0.5, 0.75, 0.90, 0.95, 0.975, 0.99],
    "max_options_expiry_days": 25,

    "external_data": {
        # Federal Funds Effective Rate (DFF)
        # https://fred.stlouisfed.org/series/DFF
        # https://github.com/deerfieldgreen/FRED_data/tree/main
        #    'link': "https://docs.google.com/spreadsheets/d/e/2PACX-1vT5lyey5dhfrZifoZFuDwlQDOz6oILyUyAHTLVe2eqiLv9jWkNeIFITIeKqwBOtS8oEUOoZ2zXX1De7/pub?gid=1400614786&single=true&output=csv",

        'dff': {
            'source': 'gsheet',
            'link': "https://raw.githubusercontent.com/deerfieldgreen/FRED_data/main/data/dff/data.csv",
            'col_date': 'date',
            'col_val': 'dff',
            'lag_days': 1,
        },

    },
}


model_settings = {
    "col_pred": ['Median','Range','Skew'],
    "model_lookback": 100,
    "prediction_lookforward_days": 1,
    "halflife_every": 5,
    "quantile_list": ['Q10', 'Q25', 'Q50', 'Q100', 'Q250', 'Q500', 'Q750', 'Q900', 'Q950', 'Q975', 'Q990'],
    "feature_mapping": {
        "Median": ['price','Median','call_back_implied_vol','put_back_implied_vol'],
        "Range": ['Range','straddle_front_premium'],
        "Skew": ['Skew'],
    },
}



