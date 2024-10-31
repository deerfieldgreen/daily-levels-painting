
from AlgorithmImports import *

import numpy as np
import pandas as pd
import math
import random
import scipy.stats as stats


def bsm_price(option_type, sigma, s, k, r, T, q):
    # calculate the bsm price of European call and put options
    d1 = (np.log(s / k) + (r - q + sigma ** 2 * 0.5) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'c':
        return np.exp(-r*T) * (s * np.exp((r - q)*T) * stats.norm.cdf(d1) - k * stats.norm.cdf(d2))
    if option_type == 'p':
        return np.exp(-r*T) * (k * stats.norm.cdf(-d2) - s * np.exp((r - q)*T) * stats.norm.cdf(-d1))
    raise Exception(f'No such option type: {option_type}')

def implied_vol(option_type, option_price, s, k, r, T, q):
    # apply bisection method to get the implied volatility by solving the BSM function
    precision = 0.00001
    upper_vol = 500.0
    max_vol = 500.0
    min_vol = 0.0001
    lower_vol = 0.0001
    iteration = 50

    while iteration > 0:
        iteration -= 1
        mid_vol = (upper_vol + lower_vol)/2
        price = bsm_price(option_type, mid_vol, s, k, r, T, q)

        if option_type == 'c':
            lower_price = bsm_price(option_type, lower_vol, s, k, r, T, q)
            if (lower_price - option_price) * (price - option_price) > 0:
                lower_vol = mid_vol
            else:
                upper_vol = mid_vol
            if mid_vol > max_vol - 5 :
                return 0.000001

        if option_type == 'p':
            upper_price = bsm_price(option_type, upper_vol, s, k, r, T, q)
            if (upper_price - option_price) * (price - option_price) > 0:
                upper_vol = mid_vol
            else:
                lower_vol = mid_vol

        if abs(price - option_price) < precision:
            break

    return mid_vol

def get_call_front_implied_vol(row):
    out = implied_vol(
        'c', row['call_front_price'], row['price'], row['call_front_strike'],
        row['dff'] / 100, (row['call_front_expiry_days'] + 1) / 365, 0
    )
    return out

def get_call_back_implied_vol(row):
    out = implied_vol(
        'c', row['call_back_price'], row['price'], row['call_back_strike'],
        row['dff'] / 100, (row['call_back_expiry_days'] + 1) / 365, 0
    )
    return out

def get_put_front_implied_vol(row):
    out = implied_vol(
        'p', row['put_front_price'], row['price'], row['put_front_strike'],
        row['dff'] / 100, (row['put_front_expiry_days'] + 1) / 365, 0
    )
    return out

def get_put_back_implied_vol(row):
    out = implied_vol(
        'p', row['put_back_price'], row['price'], row['put_back_strike'],
        row['dff'] / 100, (row['put_back_expiry_days'] + 1) / 365, 0
    )
    return out

def bsm_premium(option_type, s, k, r, T, q):
    if option_type == 'c':
        return np.exp(-r*T) * (s * np.exp((r - q)*T) - k)
    if option_type == 'p':
        return np.exp(-r*T) * (k - s * np.exp((r - q)*T))

def get_straddle_front_premium(algorithm, row):
    call_premium = (row['call_front_price'] - (row['price'] - row['call_front_strike'])) / np.sqrt(row['call_front_expiry_days'] + 1)
    put_premium = (row['put_front_price'] - (row['put_front_strike'] - row['price'])) / np.sqrt(row['put_front_expiry_days'] + 1)
    out = call_premium + put_premium
    return out

def get_straddle_back_premium(algorithm, row):
    call_premium = (row['call_back_price'] - (row['price'] - row['call_back_strike'])) / np.sqrt(row['call_back_expiry_days'] + 1)
    put_premium = (row['put_back_price'] - (row['put_back_strike'] - row['price'])) / np.sqrt(row['put_back_expiry_days'] + 1)
    out = call_premium + put_premium
    return out







