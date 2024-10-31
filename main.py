## Version
# Daily Range V 1.0
from AlgorithmImports import *
from datetime import datetime
##-##
IS_LIVE = True
TO_SAVE_DATA = True
IS_TEST_LIVE = False
##-##

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import deque
import pickle
from sklearn.linear_model import LinearRegression
import json


from config import (
    general_setting,
    model_settings,
)

from model_functions import (
    get_call_front_implied_vol,
    get_call_back_implied_vol,
    get_put_front_implied_vol,
    get_put_back_implied_vol,
    get_straddle_front_premium,
    get_straddle_back_premium,
)

from QuantConnect.DataSource import *


class DailyRangeAlgo(QCAlgorithm):

    def Initialize(self):
        self.SetTimeZone(TimeZones.NewYork)
        # self.SetStartDate(2021, 1, 1)
        self.SetStartDate(2024, 8, 1)

        self.SetCash(100000)
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        self.SetSecurityInitializer(self.SecurityInitializer)
        self.general_setting = general_setting
        self.model_settings = model_settings
        self.ref_ticker = self.general_setting["ref_ticker"]
        self.model_name = self.general_setting["model_name"]
        self.model_name_init = self.general_setting["model_name_init"]
        self.ref_hour = self.general_setting['ref_hour']
        self.ref_minute = self.general_setting['ref_minute'] 
        self.month_start_date = None
        self.last_sent_date = None
        self.ref_symbol = None
        self.IS_LIVE = IS_LIVE
        self.TO_SAVE_DATA = TO_SAVE_DATA
        self.IS_TEST_LIVE = IS_TEST_LIVE
        self.SetWarmUp(int(3 * 20 * 24 * 60), Resolution.Minute)
        #self.SetWarmUp(int(0.6*20*24*60), Resolution.Minute)

        self.nvda_split_date = datetime.strptime('2024-06-10', '%Y-%m-%d').date()

        if self.IS_TEST_LIVE:
            self.has_sent_signal = False
            self.prediction_output_list = []

        # Data Initialization
        self.symbol_ticker_map = {}
        self.ticker_symbol_map = {}
        self.ticker_data_list = {}
        self.ticker_prediction_list = {}
        for ticker in self.general_setting["tickers"]:
            if general_setting["tickers"][ticker]["type"] == "equity":
                symbol = self.AddEquity(
                    ticker,
                    Resolution.Minute,
                    dataNormalizationMode=DataNormalizationMode.Raw,
                ).Symbol

            self.symbol_ticker_map[symbol] = ticker
            self.ticker_symbol_map[ticker] = symbol
            self.ticker_data_list[ticker] = []
            self.ticker_prediction_list[ticker] = []
            if ticker == self.ref_ticker:
                self.ref_symbol = symbol

        self.Schedule.On(
            self.DateRules.EveryDay(self.ticker_symbol_map[self.ref_ticker]),
            self.TimeRules.AfterMarketOpen(self.ticker_symbol_map[self.ref_ticker]),
            self.Start_Of_Day,
        )

        self.Schedule.On(
            self.DateRules.MonthStart(self.ref_symbol),
            self.TimeRules.AfterMarketOpen(self.ref_symbol, 1),
            self.Get_Month_Start_Date,
        )


        self.external_data = {}
        for _dn in self.general_setting["external_data"]:
            self.external_data[_dn] = {}
            self.external_data[_dn]['time'] = None
            self.external_data[_dn]['value'] = None
            source = self.general_setting["external_data"][_dn]['source']

            if source == 'gsheet':
                self.Log(f"{str(self.Time)}: {_dn}: Loading Initial CSV File Data")
                link = self.general_setting["external_data"][_dn]['link']
                col_date = self.general_setting["external_data"][_dn]['col_date']
                col_val = self.general_setting["external_data"][_dn]['col_val']
                to_run = True
                while to_run:
                    try:
                        data = self.Download(link)
                        rows = []
                        for row in data.split('\n'):
                            content = row.replace('\r', '').lower().split(',')
                            if len(content) == 2:
                                rows.append(content)
                        data_df = pd.DataFrame(np.array(rows[1:]), columns=rows[0])
                        data_df[col_date] = data_df[col_date].apply(lambda s: datetime.strptime(s, '%Y-%m-%d'))
                        data_df[col_val] = data_df[col_val].astype(float)
                        self.external_data[_dn]['data'] = data_df.copy()
                        to_run = False
                    except:
                        pass

                self.Log(f"{str(self.Time)}: {_dn}: Initial CSV file Data Loaded")

        self.data_init_dict = {}
        self.start_datetime_dict = {}    
        if self.general_setting["use_init_data"]:
            ticker_data_list = pickle.loads(bytes(self.ObjectStore.ReadBytes(f"MODEL_DATA_{self.model_name_init}"))) 
            for ticker in self.general_setting["tickers"]:
                data_df = pd.DataFrame(ticker_data_list[ticker])
                self.start_datetime_dict[ticker] = data_df['datetime'].min()
                data_df.set_index('datetime', inplace=True)
                self.data_init_dict[ticker] = data_df.copy()
        else:
            for ticker in self.general_setting["tickers"]:
                self.start_datetime_dict[ticker] = pd.NaT
                self.data_init_dict[ticker] = pd.DataFrame()

        
        self.get_split_days()

    def get_split_days(self):
        self.stock_split_dict = {}

        data = self.download("https://raw.githubusercontent.com/deerfieldgreen/yfinance-scaling-system/refs/heads/main/data/stock_splits_data.csv")
        lines = data.split('\n')

        for i in range(len(lines)):
            content = lines[i].split(',')
            if len(content) == 1 or i == 0:
                continue
            ticker = content[0]
            split_date = datetime.strptime(content[1][:10], '%Y-%m-%d').date()
            split_ratio = int(float(content[2]))
            if ticker not in self.stock_split_dict:
                self.stock_split_dict[ticker] = {'split_date': split_date, 'split_ratio': split_ratio}
            else:
                last_split_date = self.stock_split_dict[ticker]['split_date']
                if split_date > last_split_date:
                    self.stock_split_dict[ticker]['split_date'] = split_date
                    self.stock_split_dict[ticker]['split_ratio'] = split_ratio


    def SecurityInitializer(self, security):
        security.SetMarketPrice(self.GetLastKnownPrice(security))
        security.SetDataNormalizationMode(DataNormalizationMode.Raw)

    def Get_Month_Start_Date(self):
        self.month_start_date = self.Time

    def Start_Of_Day(self):
        if self.IS_LIVE and (not self.IsWarmingUp):
            for _dn in self.general_setting["external_data"]:
                source = self.general_setting["external_data"][_dn]['source']
                if source == 'gsheet':
                    self.Log(f"{str(self.Time)}: {_dn}: Loading CSV File Data")
                    link = self.general_setting["external_data"][_dn]['link']
                    col_date = self.general_setting["external_data"][_dn]['col_date']
                    col_val = self.general_setting["external_data"][_dn]['col_val']
                    to_run = True
                    while to_run:
                        try:
                            data = self.Download(link)
                            rows = []
                            for row in data.split('\n'):
                                content = row.replace('\r', '').lower().split(',')
                                if len(content) == 2:
                                    rows.append(row.replace('\r', '').lower().split(','))
                            data_df = pd.DataFrame(np.array(rows[1:]), columns=rows[0])
                            data_df[col_date] = data_df[col_date].apply(lambda s: datetime.strptime(s, '%Y-%m-%d'))
                            data_df[col_val] = data_df[col_val].astype(float)
                            self.external_data[_dn]['data'] = data_df.copy()
                            to_run = False
                        except:
                            pass
                self.Log(f"{str(self.Time)}: {_dn}: CSV File Data Loaded")

        for _dn in self.general_setting["external_data"]:
            source = self.general_setting["external_data"][_dn]['source']
            if source == 'gsheet':
                col_date = self.general_setting["external_data"][_dn]['col_date']
                col_val = self.general_setting["external_data"][_dn]['col_val']
                lag_days = self.general_setting["external_data"][_dn]['lag_days']

                data = self.external_data[_dn]['data'][self.external_data[_dn]['data'][col_date] < (self.Time - timedelta(days=lag_days))]
                if len(data) > 0:
                    self.external_data[_dn]['time'] = data[col_date].values[-1]
                    self.external_data[_dn]['value'] = data[col_val].values[-1]


    def OnData(self, data):
        is_valid_time = (self.Time.hour == self.ref_hour) and (self.Time.minute == self.ref_minute)

        prediction_output_list = []
        for symbol, ticker in self.symbol_ticker_map.items():
            if not (
                data.ContainsKey(symbol)
                and data[symbol] is not None
            ):
                # self.Log(f"{self.Time}: {ticker}: data[symbol] is None !!")
                continue

            tt = "2024-07-29"
            if is_valid_time and self.Time.date() != datetime.strptime(tt, "%Y-%m-%d").date():

                # if self.general_setting["use_init_data"] & (self.Time < self.start_datetime_dict[ticker]):
                #     continue
                # elif self.general_setting["use_init_data"] & (self.Time in self.data_init_dict[ticker].index):
                #     data_dict = {}
                #     data_dict["datetime"] = self.Time
                #     data_dict.update(self.data_init_dict[ticker].loc[self.Time].to_dict())
                # else:

                contract_symbols = self.OptionChainProvider.GetOptionContractList(symbol, data.Time)
                data_dict = {}
                data_dict["datetime"] = self.Time
                data_dict["price"] = np.round(data[symbol].Price, 6)

                # External Data
                for _dn in self.general_setting["external_data"]:
                    data_dict[_dn] = self.external_data[_dn]['value']

                if data_dict['dff'] is None:
                    self.Log(f"{self.Time}: {ticker}: dff is None !!")
                    continue

                # Equity Data
                equity_df = self.History(
                    symbol,
                    start=self.Time-timedelta(days=7),
                    end=self.Time,
                    resolution=Resolution.Minute,
                    fillForward=False,
                    extendedMarketHours=False,
                    dataNormalizationMode=DataNormalizationMode.Adjusted,
                    )

                # Only need price from yesterday
                equity_df = equity_df.reset_index()
                equity_df['date'] = equity_df['time'].dt.date
                last_date = equity_df.loc[equity_df['date'] < self.Time.date(),'date'].max()
                equity_df = equity_df[equity_df['date'] == last_date]

                if len(equity_df) == 0:
                    self.Log(f"{self.Time}: {ticker}: equity_df len 0 !!")
                    continue

                # Quantiles of prices from yesterday
                for q in self.general_setting["quantile_list"]:
                    data_dict[f"Q{int(q*1000)}"] = equity_df['close'].quantile(q)

                idx_ref = equity_df['time'].dt.hour == self.ref_hour
                idx_ref = idx_ref & (equity_df['time'].dt.minute == self.ref_minute)
                if idx_ref.sum() == 0:
                    self.Log(f"{self.Time}: {ticker}: no ref_time data !! !!")
                    continue

                data_dict['equity_ref_price'] = equity_df.loc[idx_ref, 'close'].iloc[0]
                data_dict['ref_datetime'] = equity_df.loc[idx_ref, 'time'].iloc[0]
                data_dict['high'] = equity_df['high'].max()
                data_dict['low'] = equity_df['low'].min()
                data_dict['open'] = equity_df.iloc[0]['open']
                data_dict['close'] = equity_df.iloc[-1]['close']

                ref_equity_df = equity_df[equity_df['time'] > data_dict['ref_datetime']]
                data_dict['ref_high'] = ref_equity_df['high'].max()
                data_dict['ref_low'] = ref_equity_df['low'].min()
                data_dict['ref_open'] = ref_equity_df.iloc[0]['open']
                data_dict['ref_close'] = ref_equity_df.iloc[-1]['close']

                # Call Options Data
                try:
                    call_ref_df = pd.DataFrame(sorted([(s.ID.Date, s.ID.StrikePrice, s) for s in contract_symbols
                        if (s.ID.OptionRight == OptionRight.Call) and ((s.ID.Date.date() - self.Time.date()).days <= self.general_setting["max_options_expiry_days"])
                    ]), columns=['date','strike','symbol'])
                except:
                    call_ref_df = pd.DataFrame()
                    self.Log(f"{self.Time}: {ticker}: call option data error !!")
                if len(call_ref_df) == 0:
                    self.Log(f"{self.Time}: {ticker}: len(call_ref_df) == 0 !!")
                    continue

                if ticker in self.stock_split_dict and self.Time.date() < self.stock_split_dict[ticker]['split_date']:
                    split_ratio = self.stock_split_dict[ticker]['split_ratio']
                    call_ref_df['strike'] = round((call_ref_df['strike'] / split_ratio)).astype(int)


                # Only ATM calls with acceptable expirations
                call_ref_df['strike_diff'] = (call_ref_df['strike'] - data_dict["price"]).abs()
                idx = call_ref_df['strike_diff'] == call_ref_df['strike_diff'].min()
                call_ref_df = call_ref_df.loc[idx]
                call_ref_df.reset_index(drop=True, inplace=True)

                price_list = []
                for call_symbol in call_ref_df['symbol'].values:
                    try:
                        option = self.AddOptionContract(call_symbol, Resolution.Minute)
                        price = option.Price
                    except:
                        price = 0
                    if price == 0:
                        try:
                            history_df = self.History(call_symbol, 5)
                            if len(history_df) > 0:
                                price = history_df.tail(1)['close'].iloc[0]
                        except:
                            pass
                    price_list += [price]
                call_ref_df['price'] = price_list
                idx = call_ref_df['price'] != 0
                call_ref_df = call_ref_df.loc[idx]
                call_ref_df.reset_index(drop=True, inplace=True)
                call_ref_df.sort_values('date', ascending=True, inplace=True)
                call_ref_df.reset_index(drop=True, inplace=True)

                if len(call_ref_df) == 0:
                    self.Log(f"{self.Time}: {ticker}: call_ref_df len 0 due to price 0 !!")
                    continue

                data_dict['call_front_strike'] = call_ref_df.iloc[0]['strike']
                data_dict['call_front_expiry'] = call_ref_df.iloc[0]['date']
                data_dict['call_front_price'] = call_ref_df.iloc[0]['price']
                data_dict['call_front_expiry_days'] = (data_dict['call_front_expiry'].date() -self.Time.date()).days
                data_dict['call_back_strike'] = call_ref_df.iloc[-1]['strike']
                data_dict['call_back_expiry'] = call_ref_df.iloc[-1]['date']
                data_dict['call_back_price'] = call_ref_df.iloc[-1]['price']
                data_dict['call_back_expiry_days'] = (data_dict['call_back_expiry'].date() -self.Time.date()).days

                # Put Options Data
                try:
                    put_ref_df = pd.DataFrame(sorted([(s.ID.Date, s.ID.StrikePrice, s) for s in contract_symbols
                        if (s.ID.OptionRight == OptionRight.Put) and ((s.ID.Date.date() - self.Time.date()).days <= self.general_setting["max_options_expiry_days"])
                    ]), columns=['date','strike','symbol'])
                except:
                    put_ref_df = pd.DataFrame()
                    self.Log(f"{self.Time}: {ticker}: put option data error !!")
                if len(put_ref_df) == 0:
                    self.Log(f"{self.Time}: {ticker}: len(put_ref_df) == 0 !!")
                    continue

                if ticker in self.stock_split_dict and self.Time.date() < self.stock_split_dict[ticker]['split_date']:
                    split_ratio = self.stock_split_dict[ticker]['split_ratio']
                    put_ref_df['strike'] = round((put_ref_df['strike'] / split_ratio)).astype(int)


                put_ref_df['strike_diff'] = (put_ref_df['strike'] - data_dict['price']).abs()
                idx = put_ref_df['strike_diff'] == put_ref_df['strike_diff'].min()
                put_ref_df = put_ref_df.loc[idx]
                put_ref_df.reset_index(drop=True, inplace=True)

                price_list = []
                for put_symbol in put_ref_df['symbol'].values:
                    try:
                        option = self.AddOptionContract(put_symbol, Resolution.Minute)
                        price = option.Price
                    except:
                        price = 0
                    if price == 0:
                        try:
                            history_df = self.History(put_symbol, 10)
                            if len(history_df) > 0:
                                price = history_df.tail(1)['close'].iloc[0]
                        except:
                            pass
                    price_list += [price]
                put_ref_df['price'] = price_list
                idx = put_ref_df['price'] != 0
                put_ref_df = put_ref_df.loc[idx]
                put_ref_df.reset_index(drop=True, inplace=True)
                put_ref_df.sort_values('date', ascending=True, inplace=True)
                put_ref_df.reset_index(drop=True, inplace=True)
                if len(put_ref_df) == 0:
                    self.Log(f"{self.Time}: {ticker}: put_ref_df len 0 due to price 0 !!")
                    continue

                data_dict['put_front_strike'] = put_ref_df.iloc[0]['strike']
                data_dict['put_front_expiry'] = put_ref_df.iloc[0]['date']
                data_dict['put_front_price'] = put_ref_df.iloc[0]['price']
                data_dict['put_front_expiry_days'] = (data_dict['put_front_expiry'].date() -self.Time.date()).days
                data_dict['put_back_strike'] = put_ref_df.iloc[-1]['strike']
                data_dict['put_back_expiry'] = put_ref_df.iloc[-1]['date']
                data_dict['put_back_price'] = put_ref_df.iloc[-1]['price']
                data_dict['put_back_expiry_days'] = (data_dict['put_back_expiry'].date() -self.Time.date()).days

                # Implied volatlilities are on a scale of 1
                data_dict['call_front_implied_vol'] = get_call_front_implied_vol(data_dict)
                data_dict['call_back_implied_vol'] = get_call_back_implied_vol(data_dict)
                data_dict['put_front_implied_vol'] = get_put_front_implied_vol(data_dict)
                data_dict['put_back_implied_vol'] = get_put_back_implied_vol(data_dict)

                data_dict['straddle_front_premium'] = get_straddle_front_premium(self, data_dict)
                data_dict['straddle_back_premium'] = get_straddle_back_premium(self, data_dict)
                data_dict['straddle_front_premium_pct'] = data_dict['straddle_front_premium'] / data_dict['price']
                data_dict['straddle_back_premium_pct'] = data_dict['straddle_back_premium'] / data_dict['price']
                data_dict['implied_vol'] = (data_dict['call_back_implied_vol'] + data_dict['put_back_implied_vol']) / 2

                self.ticker_data_list[ticker] += [data_dict]

                # Finished with collecting yesterday's data, and use historical data with lookback window
                if len(self.ticker_data_list[ticker]) >= (self.model_settings['model_lookback']+1):
                    data_df = pd.DataFrame(self.ticker_data_list[ticker][-(self.model_settings['model_lookback']+1):])
                    data_df = data_df.dropna()
                    data_df.reset_index(drop=True, inplace=True)
                    yearly_data_df = pd.DataFrame(self.ticker_data_list[ticker][-250:])
                    yearly_data_df = yearly_data_df.dropna()
                    yearly_data_df.reset_index(drop=True, inplace=True)

                    # Tomorrow's quantiles
                    for col in self.model_settings['quantile_list']:
                        data_df[f"T{col}"] = data_df[col].shift(-self.model_settings['prediction_lookforward_days'])

                    data_df['Median'] = data_df['Q500'].values
                    data_df['Range'] = data_df['Q750'].values - data_df['Q250'].values
                    data_df['Skew'] = data_df['Q950'].values - 2 * data_df['Q500'].values + data_df['Q50'].values
                    data_df['TMedian'] = data_df['TQ500'].values
                    data_df['TRange'] = data_df['TQ750'].values - data_df['TQ250'].values
                    data_df['TSkew'] = data_df['TQ950'].values - 2 * data_df['TQ500'].values + data_df['TQ50'].values

                    model_df = data_df.head(len(data_df)-1)
                    pred_df = data_df.tail(1)

                    prediction_dict = {}
                    prediction_dict["ticker"] = ticker
                    prediction_dict["datetime"] = str(self.Time)
                    prediction_dict["spot_price"] = pred_df['price'].iloc[0]
                    prediction_dict["straddle_value"] = pred_df['straddle_front_premium'].iloc[0]
                    prediction_dict["straddle_pct_value"] = pred_df['straddle_front_premium_pct'].iloc[0]
                    prediction_dict["past_straddle_value"] = model_df['straddle_front_premium'].mean()
                    prediction_dict["past_straddle_pct_value"] = model_df['straddle_front_premium_pct'].mean()
                    prediction_dict["past_straddle_value_std"] = model_df['straddle_front_premium'].std()
                    prediction_dict["past_straddle_pct_value_std"] = model_df['straddle_front_premium_pct'].std()
                    prediction_dict["upper_value"] = prediction_dict["spot_price"] + prediction_dict["straddle_value"]
                    prediction_dict["lower_value"] = prediction_dict["spot_price"] - prediction_dict["straddle_value"]
                    prediction_dict["straddle_pct_sma10"] = data_df['straddle_front_premium_pct'].tail(10).mean()
                    prediction_dict["straddle_pct_sma20"] = data_df['straddle_front_premium_pct'].tail(20).mean()
                    prediction_dict["straddle_pct_sma30"] = data_df['straddle_front_premium_pct'].tail(30).mean()
                    prediction_dict["straddle_pct_sma50"] = data_df['straddle_front_premium_pct'].tail(50).mean()

                    implied_vol_cur = yearly_data_df.tail(1)['implied_vol'].iloc[0]
                    implied_vol_min = yearly_data_df['implied_vol'].min()
                    implied_vol_max = yearly_data_df['implied_vol'].max()
                    prediction_dict["implied_vol_rank"] = (implied_vol_cur - implied_vol_min) / (implied_vol_max - implied_vol_min)
                    prediction_dict["implied_vol_percentile"] = (yearly_data_df['implied_vol'] < implied_vol_cur).mean()

                    for col in self.model_settings['col_pred']:
                        model = None
                        model = LinearRegression(fit_intercept=True, positive=True)
                        col_feature = self.model_settings['feature_mapping'][col].copy()

                        # sample_weight = np.ones(len(model_df))
                        r = 0.5 ** (1/self.model_settings['halflife_every'])
                        a = 1.0
                        sample_weight = np.array([a*r**i for i in range(len(model_df))])
                        sample_weight = sample_weight / np.sum(sample_weight)
                        sample_weight = sample_weight[::-1]
                        model.fit(model_df[col_feature].values, model_df[f"T{col}"].values, sample_weight=sample_weight)
                        # model.fit(model_df[col_feature].values, model_df[f"T{col}"].values)

                        prediction_dict[f"P{col}"] = model.predict(pred_df[col_feature].values)[0]
                        if col == 'Range':
                            if prediction_dict[f"P{col}"] <= 0:
                                prediction_dict[f"P{col}"] = pred_df[['call_front_implied_vol','call_back_implied_vol','put_front_implied_vol','put_back_implied_vol']].mean(axis=1).values[0] * 10
                                self.debug(F'Predicted range is negative, and P_range is reconciled.')

                    prediction_dict['PVol'] = prediction_dict['PRange'] / 1.35 * 4
                    prediction_dict['PSkewAdjustment'] = prediction_dict['PSkew'] * prediction_dict['PRange']
                    prediction_dict['PMean'] = prediction_dict['PMedian'] - prediction_dict['PSkewAdjustment']
                    for band in range(1, 4):
                        prediction_dict[f'PUpper{band}'] = prediction_dict['PMean'] + band * prediction_dict['PVol']
                        prediction_dict[f'PLower{band}'] = prediction_dict['PMean'] - band * prediction_dict['PVol']

                    self.ticker_prediction_list[ticker] += [prediction_dict]
                    prediction_output_list += [prediction_dict]
                    if self.IS_TEST_LIVE:
                        self.prediction_output_list += [prediction_dict]

                if self.TO_SAVE_DATA:
                    self.ObjectStore.SaveBytes(f"MODEL_DATA_{self.model_name}", pickle.dumps(self.ticker_data_list))
                    # self.Log(f"{str(self.Time)}: Model Data Saved At: MODEL_DATA_{self.model_name}")
                    self.ObjectStore.SaveBytes(f"PREDICTION_DATA_{self.model_name}", pickle.dumps(self.ticker_prediction_list))
                    # self.Log(f"{str(self.Time)}: Prediction Data Saved At: PREDICTION_DATA_{self.model_name}")


        if self.IS_LIVE:
            if self.IS_TEST_LIVE:
                if (len(self.prediction_output_list) > 0) and (not self.has_sent_signal):
                    self.has_sent_signal = True
                    output_dict = {}
                    output_dict["auth"] = self.general_setting["auth"]
                    output_dict["prediction_output_list"] = self.prediction_output_list
                    self.Log(f"{self.Time}: {self.prediction_output_list}")
                    self.Notify.Web(self.general_setting["url"], json.dumps(output_dict))
                    self.Log(f"{self.Time}: Web Notification Sent")

            else:
                # send_web_sotification = False
                # if self.last_sent_date is None:
                #     send_web_sotification = True
                #     self.last_sent_date = self.Time.date()
                # elif self.Time.date() > self.last_sent_date:
                #     send_web_sotification = True
                #     self.last_sent_date = self.Time.date()
                # if send_web_sotification and (not self.IsWarmingUp) and is_valid_time and (len(prediction_output_list) > 0):
                if (not self.IsWarmingUp) and is_valid_time and (len(prediction_output_list) > 0):
                    output_dict = {}
                    output_dict["auth"] = self.general_setting["auth"]
                    output_dict["prediction_output_list"] = prediction_output_list

                    self.Notify.Web(self.general_setting["url"], json.dumps(output_dict))
                    self.Log(f"{self.Time}: Web Notification Sent")



