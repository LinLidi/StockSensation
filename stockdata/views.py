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

def dicopinion(request):
	return render(request,"dicopinion.html")

def nbopinion(request):
	return render(request,"nbopinion.html")

def index(request):
	a = request.GET['intext']
	a = str(a)
	model = gensim.models.word2vec.Word2Vec.load("segwords.model")
	items = model.most_similar(a,topn=10) #找出最近n各单词
	return render(request, 'echarts.html', {'items': json.dumps(items)})

def basedicf(request):
	return render(request,"basedic.html")

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

def basedic(request):
	fpge = request.GET['fpge']
	lpge= request.GET['lpge']
	fpge = int(fpge)
	lpge = int(lpge)
	if fpge < lpge:
		pass
	#设置时间空间
	allCount = [[0 for q in range(6)] for q in range(372)]
	for monthWide in range(0,12):
		for day in range(0,31):
			allCount[day+monthWide*31][0] = monthWide+1
			allCount[day+monthWide*31][1] = day+1
	#计算情绪值
	for page_num in range(fpge, lpge+1):
		url = 'http://guba.eastmoney.com/list,gssz,f_' + str(page_num) + '.html'
		request1 = urllib.request.urlopen(url)
		content = str(request1.read(),'utf-8')
		pattern = re.compile('<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>',re.S)
		items = re.findall(pattern,content)
		for date in range(0,372):
			for i in range(0,len(items)):
				#找到匹配时间
				if int(items[i][3]) == allCount[date][0] and int(items[i][4]) == allCount[date][1]:
					allCount[date][5] += 1
					#分词
					item1 = items[i][1]
					seg_list = list(jieba.cut(item1, cut_all=True))
					#匹配计数
					for eachItem in seg_list:
						if eachItem != ' ':
							if eachItem in positiveWord:
								allCount[date][2] += 1
								continue
							elif eachItem in negativeWord:
								allCount[date][3] += 1
								continue
							elif eachItem in neutralWord:
								allCount[date][4] += 1
	#打印输出，记录不全为0天数
	nonZero = 0
	for z in range(0,372):
		if (allCount[z][2])*(allCount[z][2])+(allCount[z][3])*(allCount[z][3])+(allCount[z][4])*(allCount[z][4])+(allCount[z][5])*(allCount[z][5]) !=0:
			print(allCount[z][0],"月",allCount[z][1],"日发帖总数：",allCount[z][5],"; 情绪值：[",allCount[z][2],",",allCount[z][3],",",allCount[z][4],"]")
			nonZero +=1
	return render(request,'basedicgraph.html',{'allCount':json.dumps(allCount)})


def stocksearch(request):
	#获取时间月日
	timemon = time.strftime("%m",timelocaltime())
	timeday = time.strftime("%d",timelocaltime())
	stonum = request.GET('stonum')
	url = 'http://guba.eastmoney.com/list,'+str(storcknum)+'.html'
	request2 = urllib.request.urlopen(url)
	content = str(request2.read(),'utf-8')
	pattern = re.compile('<title>(.*?)股吧_(.*?)怎么样_分析讨论社区—东方财富网</title>',re.S)
	itemstemp = re.findall(pattern,content)
	stocknam = itemstemp[1]
	for page_nume in range(0,50):
		request3 = urllib.request.urlopen(url)
		content2 = str(request3.read(),'utf-8')
		pattern2 = re.compile('<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>',re.S)
		itemstemp2 = re.findall(pattern2,content2)
		for i in range(0,len(itemstemp2)):
			if int(itemstemp2[i][3]) == int(timemon):
				stonum =1
	return(request,'sss.html')




