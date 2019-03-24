# coding:utf-8
import ssl
import requests
from urllib.parse import quote
import string
import random
import time
import hashlib
# from __future__ import unicode_literals
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
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
import os
import pprint
positiveWord = ['向上', '上涨', '涨', '涨停', '高涨', '底', '底部', '反击', '拉升', '加仓', '买入', '买', '看多', '多', '满仓', '杀入', '抄底', '绝地',
                '反弹', '反转', '突破', '牛', '牛市', '利好', '盈利', '新高', '反弹', '增', '爆发', '升', '笑', '胜利', '逆袭', '热', '惊喜', '回暖', '回调', '强']
negativeWord = ['向下', '下跌', '跌', '跌停', '低迷', '顶', '顶部', '空袭', '跳水', '减仓', '减持', '卖出', '卖', '空', '清仓', '暴跌', '亏', '阴跌', '拖累', '利空',
                '考验', '新低', '跌破', '熊', '熊市', '套', '回撤', '垃圾', '哭', '退', '减', '重挫', '平仓', '破灭', '崩', '绿', '韭菜', '悲催', '崩溃', '下滑', '拖累', '弱']
neutralWord = ['震荡', '休养', '休养生息', '谨慎', '观望', '平稳', '过渡', '盘整']

ssl._create_default_https_context = ssl._create_unverified_context
# import md5sign


def curlmd5(src):
    m = hashlib.md5(src.encode('UTF-8'))
    return m.hexdigest().upper()


def tx_npl(textstring):
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"
    time_stamp = str(int(time.time()))
    print(time_stamp)
    nonce_str = ''.join(random.sample(
        string.ascii_letters + string.digits, 10))
    print(nonce_str)
    print(len(time_stamp))
    print(len(nonce_str))
    app_id = '2108662408'
    app_key = 'PtTGCcqQ659C9kIQ'
    params = {
        'app_id': app_id,
        'text': textstring,
        'time_stamp': time_stamp,
        'nonce_str': nonce_str,
    }
    sign_before = ''
    for key in sorted(params):
        sign_before += '{}={}&'.format(key, quote(params[key], safe=''))
    sign_before += 'app_key={}'.format(app_key)
    sign = curlmd5(sign_before)
    params['sign'] = sign
    print(params['sign'])
    # plus_item = plus_item.encode('utf-8')
    # payload = md5sign.params
    r = requests.post(url, data=params)
    return r.json()


def index(request):
    return render(request, 'index.html')


def dash_index(request):
    stock_his_data = ts.get_hist_data('sz')
    stock_name = get_stock_name('sz')

    stock_his_data_dic = json.dumps(stock_his_data.to_json(orient='index'))
    pprint.pprint(stock_his_data_dic)

    print(type(stock_his_data_dic))
    date = stock_his_data.index.tolist()
    open = stock_his_data['open'].tolist()
    close = stock_his_data['close'].tolist()
    high = stock_his_data['high'].tolist()
    low = stock_his_data['low'].tolist()
    volume = stock_his_data['volume'].tolist()
    dataMA5 = stock_his_data['ma5'].tolist()
    dataMA10 = stock_his_data['ma10'].tolist()
    dataMA20 = stock_his_data['ma20'].tolist()

    return render(request, 'base_dash.html', {'stock_his_data_dic': stock_his_data_dic, 'date': json.dumps(date), 'open': json.dumps(open), 'close': json.dumps(close), 'high': json.dumps(high), 'low': json.dumps(low), 'volume': json.dumps(volume), 'dataMA5': json.dumps(dataMA5), 'dataMA10': json.dumps(dataMA10), 'dataMA20': json.dumps(dataMA20), 'stock_name': json.dumps(stock_name)})


def home(request):
    stock_his_data = ts.get_hist_data('sh000001')
    stock_name = get_stock_name('sh000001')

    date = stock_his_data.index.tolist()
    open = stock_his_data['open'].tolist()
    close = stock_his_data['close'].tolist()
    high = stock_his_data['high'].tolist()
    low = stock_his_data['low'].tolist()
    volume = stock_his_data['volume'].tolist()
    dataMA5 = stock_his_data['ma5'].tolist()
    dataMA10 = stock_his_data['ma10'].tolist()
    dataMA20 = stock_his_data['ma20'].tolist()

    return render(request, 'home.html', {'date': json.dumps(date), 'open': json.dumps(open), 'close': json.dumps(close), 'high': json.dumps(high), 'low': json.dumps(low), 'volume': json.dumps(volume), 'dataMA5': json.dumps(dataMA5), 'dataMA10': json.dumps(dataMA10), 'dataMA20': json.dumps(dataMA20), 'stock_name': json.dumps(stock_name)})


def stockKLine(request):
    stocknum = request.GET['stocknum']
    stock_his_data = ts.get_hist_data(stocknum)
    stock_name = get_stock_name(stocknum)

    date = stock_his_data.index.tolist()
    open = stock_his_data['open'].tolist()
    close = stock_his_data['close'].tolist()
    high = stock_his_data['high'].tolist()
    low = stock_his_data['low'].tolist()
    volume = stock_his_data['volume'].tolist()
    dataMA5 = stock_his_data['ma5'].tolist()
    dataMA10 = stock_his_data['ma10'].tolist()
    dataMA20 = stock_his_data['ma20'].tolist()

    dateCount = setDate()
    nb_dateCount = setDate()
    homedir = os.getcwd()

    clf = joblib.load(homedir+'/StockVisualData/Clf.pkl')
    vectorizer = joblib.load(homedir+'/StockVisualData/Vect')
    transformer = joblib.load(homedir+'/StockVisualData/Tfidf')

    for pageNum in range(1, 21):
        urlPage = 'http://guba.eastmoney.com/list,' + \
            str(stocknum)+'_'+str(pageNum)+'.html'
        stockPageRequest = urllib.request.urlopen(urlPage)
        htmlTitleContent = str(stockPageRequest.read(), 'utf-8')
        titlePattern = re.compile(
            '<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>', re.S)
        gotTitle = re.findall(titlePattern, htmlTitleContent)
        for i in range(len(gotTitle)):
            for j in range(len(dateCount)):
                if int(gotTitle[i][3]) == dateCount[j][0] and int(gotTitle[i][4]) == dateCount[j][1]:
                    dateCount[j][5] += 1
                    segList = list(jieba.cut(gotTitle[i][1], cut_all=True))
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
            text_predict = []
            for j in range(len(nb_dateCount)):
                if int(gotTitle[i][3]) == nb_dateCount[j][0] and int(gotTitle[i][4]) == nb_dateCount[j][1]:
                    nb_dateCount[j][5] += 1
                    seg_list = list(jieba.cut(gotTitle[i][1], cut_all=True))
                    seg_text = " ".join(seg_list)
                    text_predict.append(seg_text)
                    text_predict = np.array(text_predict)
                    text_frequency = vectorizer.transform(text_predict)
                    new_tfidf = transformer.transform(text_frequency)
                    predicted = clf.predict(new_tfidf)
                    if predicted == '积极':
                        nb_dateCount[j][2] += 1
                        continue
                    elif predicted == '消极':
                        nb_dateCount[j][3] += 1
                        continue
                    elif predicted == '中立':
                        nb_dateCount[j][4] += 1

    return render(request, 'Stockkline/stockKline.html', {'stock_name': json.dumps(stock_name), 'date': json.dumps(date), 'open': json.dumps(open), 'close': json.dumps(close), 'high': json.dumps(high), 'low': json.dumps(low), 'volume': json.dumps(volume), 'dataMA5': json.dumps(dataMA5), 'dataMA10': json.dumps(dataMA10), 'dataMA20': json.dumps(dataMA20), 'dateCount': json.dumps(dateCount), 'nb_dateCount': json.dumps(nb_dateCount)})


def wordcloud(request):
    return render(request, "wordcloud.html")


def wordcloudResult(request):
    return render(request, "wordcloudResult.html")


def dicopinion(request):
    return render(request, "dicopinion.html")


def dicopinionResult(request):
    dicStockNum = request.GET['dicStockNum']
    dateCount = setDate()
    stock_name = get_stock_name(dicStockNum)

    for pageNum in range(1, 10):
        urlPage = 'http://guba.eastmoney.com/list,' + \
            str(dicStockNum)+',f_'+str(pageNum)+'.html'
        stockPageRequest = urllib.request.urlopen(urlPage)
        htmlTitleContent = str(stockPageRequest.read(), 'utf-8')
        titlePattern = re.compile(
            '<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>', re.S)
        gotTitle = re.findall(titlePattern, htmlTitleContent)
        print(type(gotTitle))
        for i in range(len(gotTitle)):
            for j in range(len(dateCount)):
                if int(gotTitle[i][3]) == dateCount[j][0] and int(gotTitle[i][4]) == dateCount[j][1]:
                    dateCount[j][5] += 1
                    segList = list(jieba.cut(gotTitle[i][1], cut_all=True))
                    # print(tx_npl(gotTitle[i][1]))
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
    return render(request, 'dicopinionResult.html', {'stock_name': stock_name, 'dateCount': json.dumps(dateCount)})


def nbopinion(request):
    return render(request, "nbopinion.html")


def nbopinionResult(request):
    Nb_stock_number = request.GET['Nb_stock_number']
    dateCount = setDate()
    stock_name = get_stock_name(Nb_stock_number)
    homedir = os.getcwd()

    clf = joblib.load(homedir+'/StockVisualData/Clf.pkl')
    vectorizer = joblib.load(homedir+'/StockVisualData/Vect')
    transformer = joblib.load(homedir+'/StockVisualData/Tfidf')

    for pageNum in range(1, 21):
        urlPage = 'http://guba.eastmoney.com/list,' + \
            str(Nb_stock_number)+'_'+str(pageNum)+'.html'
        stockPageRequest = urllib.request.urlopen(urlPage)
        htmlTitleContent = str(stockPageRequest.read(), 'utf-8')
        titlePattern = re.compile(
            '<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>', re.S)
        gotTitle = re.findall(titlePattern, htmlTitleContent)
        for i in range(len(gotTitle)):
            text_predict = []
            for j in range(len(dateCount)):
                if int(gotTitle[i][3]) == dateCount[j][0] and int(gotTitle[i][4]) == dateCount[j][1]:
                    dateCount[j][5] += 1
                    seg_list = list(jieba.cut(gotTitle[i][1], cut_all=True))
                    seg_text = " ".join(seg_list)
                    text_predict.append(seg_text)
                    text_predict = np.array(text_predict)
                    text_frequency = vectorizer.transform(text_predict)
                    new_tfidf = transformer.transform(text_frequency)
                    predicted = clf.predict(new_tfidf)
                    if predicted == '积极':
                        dateCount[j][2] += 1
                        continue
                    elif predicted == '消极':
                        dateCount[j][3] += 1
                        continue
                    elif predicted == '中立':
                        dateCount[j][4] += 1
    return render(request, 'nbopinionResult.html', {'stock_name': stock_name, 'dateCount': json.dumps(dateCount)})

# 设置时间数组


def setDate():
    dateCount = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [
        0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
    for i in range(5):
        dateCount[i][0] = (datetime.datetime.today() -
                           datetime.date.resolution * i).month
        dateCount[i][1] = (datetime.datetime.today() -
                           datetime.date.resolution * i).day
    return dateCount

# 获取股票名称


def get_stock_name(stocknumber):
    realtimeData = ts.get_realtime_quotes(stocknumber)
    realtimeData = realtimeData.to_dict('record')
    stock_name = realtimeData[0]['name']
    return stock_name

# 获取分词List


def get_segList(stocknumber):
    segList = []
    for pageNum in range(1, 21):
        urlPage = 'http://guba.eastmoney.com/list,' + \
            str(stocknumber) + '_' + str(pageNum) + '.html'
        stockPageRequest = urllib.request.urlopen(urlPage)
        htmlTitleContent = str(stockPageRequest.read(), 'utf-8')
        titlePattern = re.compile(
            '<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>', re.S)
        gotTitle = re.findall(titlePattern, htmlTitleContent)
        for i in range(len(gotTitle)):
            for j in range(len(dateCount)):
                if int(gotTitle[i][3]) == dateCount[j][0] and int(gotTitle[i][4]) == dateCount[j][1]:
                    segSentence = list(jieba.cut(gotTitle[i][1], cut_all=True))
                    segList.append(segSentence)
    return segList

# 分类器构建和数据持久化


def NB_create_model():
    # 获取标题文本
    text_list = []
    for page_num in range(0, 5):
        # 页数可改
        url = 'http://guba.eastmoney.com/list,gssz,f_' + \
            str(page_num) + '.html'
        request = urllib.request.urlopen(url)
        content = str(request.read(), 'utf-8')
        pattern = re.compile(
            '<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>', re.S)
        itemstemp = re.findall(pattern, content)
        for i in range(0, len(itemstemp)):
            seg_list = list(jieba.cut(itemstemp[i][1], cut_all=False))
            seg_str = " ".join(seg_list)
            text_list.append(seg_str)
    text_list = np.array(text_list)

    # 标注文本特征
    class_vec = [' ']*len(text_list)
    for i in range(0, len(text_list)):
        for pos in positiveWord:
            if pos in text_list[i]:
                class_vec[i] = '积极'
        for neg in negativeWord:
            if neg in text_list[i]:
                class_vec[i] = '消极'
        for neu in neutralWord:
            if neu in text_list[i]:
                class_vec[i] = '中立'
        if class_vec[i] == ' ':
            class_vec[i] = '无立场'

    # 将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()
    # 该类会统计每个词语的tf-idf权值
    transformer = TfidfTransformer()
    # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    tfidf = transformer.fit_transform(vectorizer.fit_transform(text_list))

    # 构造分类器
    clf = MultinomialNB()
    clf.fit(tfidf, class_vec)

    # 持久化保存
    joblib.dump(clf, 'Clf.pkl')
    joblib.dump(vectorizer, 'Vect')
    joblib.dump(transformer, 'Tf-Idf')
