# coding:utf-8
from __future__ import unicode_literals
import math
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import loader
import urllib.request
import re
import jieba
import numpy as np
import gensim
import json
import datetime
import tushare as ts
import lxml
import bs4

# Create your views here.
positiveWord = ['向上', '上涨', '涨', '涨停', '高涨', '底', '底部', '反击', '拉升', '加仓', '买入', '买', '看多', '多', '满仓', '杀入', '抄底', '绝地','反弹', '反转', '突破', '牛', '牛市', '利好', '盈利', '新高', '反弹', '增', '爆发', '升', '笑', '胜利', '逆袭', '热', '惊喜', '回暖','回调', '强']
negativeWord = ['向下', '下跌', '跌', '跌停', '低迷', '顶', '顶部', '空袭', '跳水', '减仓', '减持', '卖出', '卖', '空', '清仓', '暴跌', '亏', '阴跌','拖累', '利空', '考验', '新低', '跌破', '熊', '熊市', '套', '回撤', '垃圾', '哭', '退', '减', '重挫', '平仓', '破灭', '崩', '绿','韭菜', '悲催', '崩溃', '下滑', '拖累', '弱']
neutralWord = ['震荡', '休养', '休养生息', '谨慎', '观望', '平稳', '过渡', '盘整']

def home(request):
    tf = ts.get_hist_data('sh000001')
    df = ts.get_realtime_quotes('sh000001')
    df = df.to_dict('record')
    stockname = df[0]['name']
    date = tf.index.tolist()
    open = tf['open']
    open = open.tolist()
    close = tf['close']
    close = close.tolist()
    high = tf['high']
    high = high.tolist()
    low = tf['low']
    low = low.tolist()
    volume = tf['volume']
    volume = volume.tolist()
    dataMA5 = tf['ma5']
    dataMA5 = dataMA5.tolist()
    dataMA10 = tf['ma10']
    dataMA10 = dataMA10.tolist()
    dataMA20 = tf['ma20']
    dataMA20 = dataMA20.tolist()
    return render(request,'home.html',{'date':json.dumps(date),'open':json.dumps(open),'close':json.dumps(close),'high':json.dumps(high),'low':json.dumps(low),'volume':json.dumps(volume),'dataMA5':json.dumps(dataMA5),'dataMA10':json.dumps(dataMA10),'dataMA20':json.dumps(dataMA20),'stockname':json.dumps(stockname)})

def stockKLine(request):
    stocknum = request.GET['stocknum']
    tf = ts.get_hist_data(stocknum)
    df = ts.get_realtime_quotes(stocknum)
    df = df.to_dict('record')
    stockname = df[0]['name']
    date = tf.index.tolist()
    open = tf['open']
    open = open.tolist()
    close = tf['close']
    close = close.tolist()
    high = tf['high']
    high = high.tolist()
    low = tf['low']
    low = low.tolist()
    volume = tf['volume']
    volume = volume.tolist()
    dataMA5 = tf['ma5']
    dataMA5 = dataMA5.tolist()
    dataMA10 = tf['ma10']
    dataMA10 = dataMA10.tolist()
    dataMA20 = tf['ma20']
    dataMA20 = dataMA20.tolist()
    return render(request,'stockKline.html',{'stockname':json.dumps(stockname),'date':json.dumps(date),'open':json.dumps(open),'close':json.dumps(close),'high':json.dumps(high),'low':json.dumps(low),'volume':json.dumps(volume),'dataMA5':json.dumps(dataMA5),'dataMA10':json.dumps(dataMA10),'dataMA20':json.dumps(dataMA20)})

def wordcloud(request):
    return render(request,"wordcloud.html")

def wordcloudResult(request):
    return render(request,"wordcloudResult.html")

def dicopinion(request):
    return render(request,"dicopinion.html")

def dicopinionResult(request):
    dicStockNum = request.GET['dicStockNum']
    dateCount = setDate()

    stockName = getStockName(dicStockNum)
    
    for pageNum in range(1,21):
        urlPage = 'http://guba.eastmoney.com/list,'+str(dicStockNum)+'_'+str(pageNum)+'.html'
        stockPageRequest = urllib.request.urlopen(urlPage)
        htmlTitleContent = str(stockPageRequest.read(),'utf-8')
        titlePattern = re.compile('<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>',re.S)
        gotTitle = re.findall(titlePattern,htmlTitleContent)
        for i in range(len(gotTitle)):
            for j in range(len(dateCount)):
                if int(gotTitle[i][3]) == dateCount[j][0] and int(gotTitle[i][4]) == dateCount[j][1]:
                    segTitle = gotTitle[i][1]
                    segList = list(jieba.cut(segTitle, cut_all=True))
                    for eachItem in segList:
                        if eachItem != ' ':
                            if eachItem in positiveWord:
                                dateCount[j][2] += 1
                                continue
                            elif eachItem in negativeWord:
                                dateCount[j][3] += 1
                                continue
                            elif eachItem in neutralWord:
                                dateCount[j][4] += 1
    print(dateCount)
    return render(request,'dicopinionResult.html',{'stockName':stockName,'dateCount':json.dumps(dateCount)})

def nbopinion(request):
    return render(request,"nbopinion.html")

def nbopinionResult(request):
    stocknum = request.GET['stocknum']
    url = 'http://guba.eastmoney.com/list,'+str(stocknum)+',f.html'
    today = datetime.datetime.now()
    t_month = today.month
    t_day = today.day
    for page_num in range(0,50):
        requesturl = urllib.request.urlopen(url)
        content = str(requesturl.read(),'utf-8')
        pattern = re.compile('<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>',re.S)
        items = re.findall(pattern,content)
    return render(request,"nbopinionResult.html")

#设置时间数组
def setDate():
    dateCount = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    for i in range(5):
        dateCount[i][0] = (datetime.datetime.today()-datetime.date.resolution * i).month
        dateCount[i][1] = (datetime.datetime.today()-datetime.date.resolution * i).day
    return dateCount

#获取股票名称
def getStockName(stocknumber):
    realtimeData = ts.get_realtime_quotes(stocknumber)
    realtimeData = realtimeData.to_dict('record')
    stockName = realtimeData[0]['name']
    return stockName

#获取分词List
def getSegList(stocknumber):
    segList = []
    for pageNum in range(1, 21):
        urlPage = 'http://guba.eastmoney.com/list,' + str(stocknumber) + '_' + str(pageNum) + '.html'
        stockPageRequest = urllib.request.urlopen(urlPage)
        htmlTitleContent = str(stockPageRequest.read(), 'utf-8')
        titlePattern = re.compile('<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>', re.S)
        gotTitle = re.findall(titlePattern, htmlTitleContent)
        print(len(gotTitle))
        for i in range(len(gotTitle)):
            for j in range(len(dateCount)):
                if int(gotTitle[i][3]) == dateCount[j][0] and int(gotTitle[i][4]) == dateCount[j][1]:
                    segSentence = list(jieba.cut(gotTitle[i][1], cut_all=True))
                    segList.append(segSentence)
    return segList




