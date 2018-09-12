from django.shortcuts import render

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

    for pageNum in range(1,21):
        urlPage = 'http://guba.eastmoney.com/list,'+str(stocknum)+'_'+str(pageNum)+'.html'
        stockPageRequest = urllib.request.urlopen(urlPage)
        htmlTitleContent = str(stockPageRequest.read(),'utf-8')
        titlePattern = re.compile('<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>',re.S)
        gotTitle = re.findall(titlePattern,htmlTitleContent)
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

    return render(request,'stockKline.html',{'stock_name':json.dumps(stock_name),'date':json.dumps(date),'open':json.dumps(open),'close':json.dumps(close),'high':json.dumps(high),'low':json.dumps(low),'volume':json.dumps(volume),'dataMA5':json.dumps(dataMA5),'dataMA10':json.dumps(dataMA10),'dataMA20':json.dumps(dataMA20),'dateCount':json.dumps(dateCount),'nb_dateCount':json.dumps(nb_dateCount)})