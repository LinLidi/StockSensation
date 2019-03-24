from django.shortcuts import render
import pandas as pd
import tushare as ts
import json

#----------------------------- Necessary Methods -----------------------------#

def get_stock_name(stock_code):
    real_time_data = ts.get_realtime_quotes(stock_code).to_dict('record')
    stock_name = real_time_data[0]['name']
    return stock_name

def stock_his_data2json(stock_code):
    stock_name = get_stock_name(stock_code)
    stock_his_data_json = json.dumps(ts.get_hist_data(stock_code).to_json(orient='index'))
    return stock_name,stock_his_data_json

#----------------------------- Request Methos -----------------------------#

def home(request):
    stock_name,stock_his_data = stock_his_data2json('sh000001')
    return render(request,'base_dash.html',{'stock_name':json.dumps(stock_name),'stock_his_data':stock_his_data})
    