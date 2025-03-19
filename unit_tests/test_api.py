# Author: ABHISHEK GUPTA <abhishek@quantgrade.com>

# Purpose: To test api by sending a post request to the api

import warnings

import pandas as pd

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None) # to ensure console display all columns
pd.set_option('display.float_format', '{:0.3f}'.format)
pd.set_option('display.max_row', 50)

import requests
from unit_tests.data import data_thirteen, sample_historical_data_dict

url = 'https://daily-levels-painting-test-fvnqwgrq6q-uc.a.run.app'
# url = 'https://5e80-34-122-239-102.ngrok-free.app/'
res = requests.get(url)
print(res.text)

url = 'https://daily-levels-painting-fvnqwgrq6q-uc.a.run.app/test'
# url = 'https://5e80-34-122-239-102.ngrok-free.app/test'
res = requests.post(url)
print(res.text)

url = 'https://5e80-34-122-239-102.ngrok-free.app/webhook'
prediction_output_list = data_thirteen
# prediction_output_list = [{"A": 5, "B": 7}, {"C": 4, "B": 8}]
# prediction_output_list = [
#     {'ticker': 'QQQ', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 429.04, 'straddle_value': 14.674999999999999, 'straddle_pct_value': 0.03420426999813537, 'past_straddle_value': 3.03558312267761, 'past_straddle_pct_value': 0.0071582930131969145, 'past_straddle_value_std': 1.658686804633421, 'past_straddle_pct_value_std': 0.0038714807184218776, 'upper_value': 443.71500000000003, 'lower_value': 414.365, 'PMedian': 438.6131081809215, 'PRange': 2.6777813854575188, 'PSkew': -0.33754791380513294, 'PVol': 7.934167068022277, 'PSkewAdjustment': -0.903879520287404, 'PMean': 439.51698770120885, 'PUpper1': 447.45115476923115, 'PLower1': 431.58282063318654, 'PUpper2': 455.3853218372534, 'PLower2': 423.6486535651643, 'PUpper3': 463.3194889052757, 'PLower3': 415.714486497142},
#     {'ticker': 'SPY', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 506.9, 'straddle_value': 12.315, 'straddle_pct_value': 0.02429473268889327, 'past_straddle_value': 2.5009125491125395, 'past_straddle_pct_value': 0.005054190999220102, 'past_straddle_value_std': 1.547682080308849, 'past_straddle_pct_value_std': 0.0030469620417207504, 'upper_value': 519.215, 'lower_value': 494.585, 'PMedian': 512.0829152362401, 'PRange': 2.280180864696143, 'PSkew': 0.026060015032684847, 'PVol': 6.7560914509515335, 'PSkewAdjustment': 0.059421547611221814, 'PMean': 512.0234936886288, 'PUpper1': 518.7795851395804, 'PLower1': 505.2674022376773, 'PUpper2': 525.5356765905319, 'PLower2': 498.51131078672574, 'PUpper3': 532.2917680414835, 'PLower3': 491.75521933577426},
#     {'ticker': 'NVDA', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 836.98, 'straddle_value': 46.707636777440726, 'straddle_pct_value': 0.05580496162087592, 'past_straddle_value': 14.096553378692645, 'past_straddle_pct_value': 0.019332284233458282, 'past_straddle_value_std': 8.461612338700542, 'past_straddle_pct_value_std': 0.009038702034345163, 'upper_value': 883.6876367774407, 'lower_value': 790.2723632225593, 'PMedian': 854.614305055681, 'PRange': 25.17918430974025, 'PSkew': -3.1032535368810663, 'PVol': 74.60499054737852, 'PSkewAdjustment': -78.13739276498168, 'PMean': 932.7516978206627, 'PUpper1': 1007.3566883680412, 'PLower1': 858.1467072732842, 'PUpper2': 1081.9616789154197, 'PLower2': 783.5417167259056, 'PUpper3': 1156.5666694627982, 'PLower3': 708.9367261785271},
#     {'ticker': 'TSLA', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 158.4, 'straddle_value': 9.393488879715212, 'straddle_pct_value': 0.05930232878608088, 'past_straddle_value': 4.368015405730735, 'past_straddle_pct_value': 0.022370877405305686, 'past_straddle_value_std': 1.379460068886109, 'past_straddle_pct_value_std': 0.009693148622839567, 'upper_value': 167.79348887971523, 'lower_value': 149.00651112028478, 'PMedian': 159.99822462202906, 'PRange': 1.4018458545392454, 'PSkew': -0.31645706390931694, 'PVol': 4.153617346782949, 'PSkewAdjustment': -0.44362402318093697, 'PMean': 160.44184864521, 'PUpper1': 164.59546599199294, 'PLower1': 156.28823129842706, 'PUpper2': 168.7490833387759, 'PLower2': 152.1346139516441, 'PUpper3': 172.90270068555884, 'PLower3': 147.98099660486116},
#     {'ticker': 'BABA', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 73.82, 'straddle_value': 2.950259875558988, 'straddle_pct_value': 0.03996559029475736, 'past_straddle_value': 1.0879107723112302, 'past_straddle_pct_value': 0.014885784112014529, 'past_straddle_value_std': 0.2914672720840963, 'past_straddle_pct_value_std': 0.003964904526886753, 'upper_value': 76.77025987555898, 'lower_value': 70.86974012444101, 'PMedian': 76.29552337971356, 'PRange': 0.3096125791728552, 'PSkew': -0.012643671002473152, 'PVol': 0.9173706049566078, 'PSkewAdjustment': -0.003914639589288752, 'PMean': 76.29943801930284, 'PUpper1': 77.21680862425944, 'PLower1': 75.38206741434624, 'PUpper2': 78.13417922921606, 'PLower2': 74.46469680938962, 'PUpper3': 79.05154983417266, 'PLower3': 73.54732620443302},
#     {'ticker': 'META', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 505.31, 'straddle_value': 28.20356064991322, 'straddle_pct_value': 0.05581437266215436, 'past_straddle_value': 6.532496910943804, 'past_straddle_pct_value': 0.01488891369637143, 'past_straddle_value_std': 3.6276977985512833, 'past_straddle_pct_value_std': 0.007521504598235756, 'upper_value': 533.5135606499132, 'lower_value': 477.10643935008676, 'PMedian': 503.6609122685393, 'PRange': 4.898102239592085, 'PSkew': 0.47844439339717854, 'PVol': 14.512895524717287, 'PSkewAdjustment': 2.3434695548189963, 'PMean': 501.31744271372025, 'PUpper1': 515.8303382384375, 'PLower1': 486.80454718900296, 'PUpper2': 530.3432337631548, 'PLower2': 472.29165166428567, 'PUpper3': 544.8561292878721, 'PLower3': 457.7787561395684},
#     {'ticker': 'AMZN', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 180.17, 'straddle_value': 4.422503061992534, 'straddle_pct_value': 0.024546278858814087, 'past_straddle_value': 2.081788584502251, 'past_straddle_pct_value': 0.012556669149052083, 'past_straddle_value_std': 1.0797653860875092, 'past_straddle_pct_value_std': 0.006490362200293299, 'upper_value': 184.59250306199252, 'lower_value': 175.74749693800746, 'PMedian': 179.90008648188808, 'PRange': 1.7025627966013166, 'PSkew': 0.11938842604022762, 'PVol': 5.044630508448345, 'PSkewAdjustment': 0.20326629252087938, 'PMean': 179.6968201893672, 'PUpper1': 184.74145069781554, 'PLower1': 174.65218968091887, 'PUpper2': 189.7860812062639, 'PLower2': 169.6075591724705, 'PUpper3': 194.83071171471224, 'PLower3': 164.56292866402217},
#     {'ticker': 'TLT', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 88.545, 'straddle_value': 0.8804591605141794, 'straddle_pct_value': 0.009943634993666264, 'past_straddle_value': 0.6085632278787025, 'past_straddle_pct_value': 0.006482690100665084, 'past_straddle_value_std': 0.22535482128911585, 'past_straddle_pct_value_std': 0.0025381212028367964, 'upper_value': 89.42545916051418, 'lower_value': 87.66454083948582, 'PMedian': 88.7244918908692, 'PRange': 0.21181196037422775, 'PSkew': -0.03867456898742843, 'PVol': 0.6275909937014156, 'PSkewAdjustment': -0.008191736273855528, 'PMean': 88.73268362714306, 'PUpper1': 89.36027462084448, 'PLower1': 88.10509263344164, 'PUpper2': 89.9878656145459, 'PLower2': 87.47750163974023, 'PUpper3': 90.61545660824731, 'PLower3': 86.84991064603881},
#     {'ticker': 'GLD', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 215.05, 'straddle_value': 4.064545895094965, 'straddle_pct_value': 0.01890046917040207, 'past_straddle_value': 1.241612404481853, 'past_straddle_pct_value': 0.006225529404237414, 'past_straddle_value_std': 0.748693554676898, 'past_straddle_pct_value_std': 0.003264230215852226, 'upper_value': 219.11454589509498, 'lower_value': 210.98545410490505, 'PMedian': 215.36435603470596, 'PRange': 0.7479718443004779, 'PSkew': 0.022696411545896834, 'PVol': 2.216212872001416, 'PSkewAdjustment': 0.016976276802987116, 'PMean': 215.34737975790298, 'PUpper1': 217.5635926299044, 'PLower1': 213.13116688590156, 'PUpper2': 219.77980550190583, 'PLower2': 210.91495401390014, 'PUpper3': 221.99601837390725, 'PLower3': 208.69874114189872},
#     {'ticker': 'SLV', 'datetime': '2024-04-24 09:39:00.134533', 'spot_price': 24.96, 'straddle_value': 1.335, 'straddle_pct_value': 0.05348557692307692, 'past_straddle_value': 0.28628935587669024, 'past_straddle_pct_value': 0.012578205810027937, 'past_straddle_value_std': 0.190746000602463, 'past_straddle_pct_value_std': 0.007058943905712155, 'upper_value': 26.295, 'lower_value': 23.625, 'PMedian': 24.873541779068358, 'PRange': 0.1718607921958569, 'PSkew': 0.014302217021952134, 'PVol': 0.5092171620617982, 'PSkewAdjustment': 0.002457990347549763, 'PMean': 24.871083788720806, 'PUpper1': 25.380300950782605, 'PLower1': 24.36186662665901, 'PUpper2': 25.889518112844403, 'PLower2': 23.85264946459721, 'PUpper3': 26.3987352749062, 'PLower3': 23.343432302535412}
# ]
data_dict = {}
data_dict["auth"] = "siycfsYts$dr7kv135bd&"
data_dict["prediction_output_list"] = data_thirteen
res = requests.post(url, json=data_dict)
print(res.text)



url = 'http://localhost:8080/'
res = requests.get(url)
print(res.text)

url = 'http://localhost:8080/test'
res = requests.post(url)
print(res.text)


url = 'https://daily-levels-painting-test-fvnqwgrq6q-uc.a.run.app/webhook'
url = 'http://localhost:8080/webhook'
prediction_output_list = [
    # {'ticker': 'QQQ', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 443.04, 'straddle_value': 5.52, 'straddle_pct_value': 0.01245937161430119, 'past_straddle_value': 2.573225521540213, 'past_straddle_pct_value': 0.00646344209941568, 'past_straddle_value_std': 0.49780409276880244, 'past_straddle_pct_value_std': 0.0014230299405164398, 'upper_value': 448.56, 'lower_value': 437.52000000000004, 'PMedian': 443.2716252104225, 'PRange': 2.8173025452365312, 'PSkew': -0.013217239721080694, 'PVol': 8.34756309699713, 'PSkewAdjustment': -0.037236963107202016, 'PMean': 443.3088621735297, 'PUpper1': 451.6564252705268, 'PLower1': 434.96129907653255, 'PUpper2': 460.00398836752396, 'PLower2': 426.6137359795354, 'PUpper3': 468.3515514645211, 'PLower3': 418.2661728825383},
    {'ticker': 'SPY', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 513.43, 'straddle_value': 4.275, 'straddle_pct_value': 0.008326354128118732, 'past_straddle_value': 2.1594637594604857, 'past_straddle_pct_value': 0.004658875404418762, 'past_straddle_value_std': 0.5067306798277208, 'past_straddle_pct_value_std': 0.0012263194547182063, 'upper_value': 517.7049999999999, 'lower_value': 509.155, 'PMedian': 514.2139540856421, 'PRange': 1.71250271494111, 'PSkew': -0.020273870410084428, 'PVol': 5.0740821183440294, 'PSkewAdjustment': -0.03471905811963382, 'PMean': 514.2486731437617, 'PUpper1': 519.3227552621057, 'PLower1': 509.17459102541767, 'PUpper2': 524.3968373804498, 'PLower2': 504.1005089070737, 'PUpper3': 529.4709194987938, 'PLower3': 499.0264267887296},
    {'ticker': 'NVDA', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 906.81, 'straddle_value': 42.86834860943444, 'straddle_pct_value': 0.047273793418063814, 'past_straddle_value': 9.987175558928115, 'past_straddle_pct_value': 0.01758827682045067, 'past_straddle_value_std': 5.983809814056536, 'past_straddle_pct_value_std': 0.007666705819842056, 'upper_value': 949.6783486094344, 'lower_value': 863.9416513905655, 'PMedian': 911.5748264776588, 'PRange': 8.47962944011947, 'PSkew': -1.6235245995423455, 'PVol': 25.124827970724358, 'PSkewAdjustment': -13.766886991037447, 'PMean': 925.3417134686963, 'PUpper1': 950.4665414394207, 'PLower1': 900.2168854979719, 'PUpper2': 975.591369410145, 'PLower2': 875.0920575272476, 'PUpper3': 1000.7161973808694, 'PLower3': 849.9672295565232},
    # {'ticker': 'TSLA', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 179.53, 'straddle_value': 7.647359838532511, 'straddle_pct_value': 0.04259655677899243, 'past_straddle_value': 4.532520020261404, 'past_straddle_pct_value': 0.02061757169054947, 'past_straddle_value_std': 1.0134264530406631, 'past_straddle_pct_value_std': 0.004531522721300805, 'upper_value': 187.1773598385325, 'lower_value': 171.8826401614675, 'PMedian': 178.4205227564817, 'PRange': 1.8435975048366482, 'PSkew': 0.23918665861274901, 'PVol': 5.46251112544192, 'PSkewAdjustment': 0.44096392700867926, 'PMean': 177.979558829473, 'PUpper1': 183.44206995491493, 'PLower1': 172.51704770403109, 'PUpper2': 188.90458108035685, 'PLower2': 167.05453657858916, 'PUpper3': 194.36709220579877, 'PLower3': 161.59202545314724},
    # {'ticker': 'SNAP', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 11.735, 'straddle_value': 0.4631549416771887, 'straddle_pct_value': 0.03946782630397858, 'past_straddle_value': 0.35183185986961535, 'past_straddle_pct_value': 0.026400416218668205, 'past_straddle_value_std': 0.22566743665629796, 'past_straddle_pct_value_std': 0.015150324174110828, 'upper_value': 12.198154941677188, 'lower_value': 11.27184505832281, 'PMedian': 11.332375724522661, 'PRange': 0.15129900191432152, 'PSkew': -0.020959631445286505, 'PVol': 0.4482933390053971, 'PSkewAdjustment': -0.0031711713181638767, 'PMean': 11.335546895840825, 'PUpper1': 11.783840234846222, 'PLower1': 10.887253556835427, 'PUpper2': 12.232133573851618, 'PLower2': 10.438960217830031, 'PUpper3': 12.680426912857016, 'PLower3': 9.990666878824634},
    # {'ticker': 'HOOD', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 16.365, 'straddle_value': 0.6929646455628166, 'straddle_pct_value': 0.04234431075849781, 'past_straddle_value': 0.2901852942883793, 'past_straddle_pct_value': 0.025598592012345763, 'past_straddle_value_std': 0.12221999185701421, 'past_straddle_pct_value_std': 0.00814159214984336, 'upper_value': 17.057964645562816, 'lower_value': 15.672035354437181, 'PMedian': 16.459381874794346, 'PRange': 0.25537787199105844, 'PSkew': -0.03807438599640431, 'PVol': 0.7566751762698027, 'PSkewAdjustment': -0.009723355673127888, 'PMean': 16.469105230467473, 'PUpper1': 17.225780406737275, 'PLower1': 15.712430054197672, 'PUpper2': 17.98245558300708, 'PLower2': 14.955754877927868, 'PUpper3': 18.739130759276883, 'PLower3': 14.199079701658064},
    # {'ticker': 'BABA', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 71.91, 'straddle_value': 1.8985817074858802, 'straddle_pct_value': 0.026402193123152277, 'past_straddle_value': 1.1616644855021938, 'past_straddle_pct_value': 0.015243311335408944, 'past_straddle_value_std': 0.33857460515443016, 'past_straddle_pct_value_std': 0.004226810410869178, 'upper_value': 73.80858170748587, 'lower_value': 70.01141829251412, 'PMedian': 72.18820538278543, 'PRange': 0.49402438845530056, 'PSkew': 0.05604951076072272, 'PVol': 1.463775965793483, 'PSkewAdjustment': 0.02768982527678483, 'PMean': 72.16051555750865, 'PUpper1': 73.62429152330213, 'PLower1': 70.69673959171516, 'PUpper2': 75.08806748909561, 'PLower2': 69.23296362592168, 'PUpper3': 76.5518434548891, 'PLower3': 67.7691876601282},
    # {'ticker': 'PYPL', 'datetime': '2024-03-07 09:39:00.100058', 'spot_price': 58.36, 'straddle_value': 1.8526197667087543, 'straddle_pct_value': 0.031744684145112306, 'past_straddle_value': 1.0382232037773418, 'past_straddle_pct_value': 0.017694296419325756, 'past_straddle_value_std': 0.48140532760688215, 'past_straddle_pct_value_std': 0.00824641079631678, 'upper_value': 60.212619766708755, 'lower_value': 56.507380233291244, 'PMedian': 58.64256446511282, 'PRange': 0.4554660474700482, 'PSkew': 0.10161399491546214, 'PVol': 1.3495290295408835, 'PSkewAdjustment': 0.04628172463178711, 'PMean': 58.59628274048103, 'PUpper1': 59.94581177002191, 'PLower1': 57.24675371094015, 'PUpper2': 61.295340799562794, 'PLower2': 55.897224681399265, 'PUpper3': 62.64486982910368, 'PLower3': 54.547695651858376},
]


# for large data
url = 'http://localhost:8080/historical'
url = 'http://localhost:8080/daily'
url = 'https://historical-dailyrange.deerfieldgreen.com/historical'
url = 'https://historical-dailyrange.deerfieldgreen.com/daily'

data_dict = {}
data_dict["auth"] = "siycfsYts$dr7kv135bd&"
data_dict["prediction_output_list"] = prediction_output_list
data_dict["prediction_output_list"] = data_thirteen
# sample_historical_data_dict['webhook_payload'] = sample_historical_data_dict['webhook_payload']*200
data_dict = sample_historical_data_dict
data_dict["dataset_type"] = "prediction"
data_dict["dataset_type"] = "model"
res = requests.post(url, json=data_dict)
print(res.text)



