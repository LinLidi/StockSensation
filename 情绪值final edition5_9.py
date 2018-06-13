"People's mind in the market"
import urllib.request
import re
import jieba
import xlwt
positiveWord = ['向上', '上涨', '涨', '涨停', '高涨', '底', '底部', '反击', '拉升', '加仓', '买入', '买', '看多', '多', '满仓', '杀入', '抄底', '绝地',
                '反弹', '反转', '突破', '牛', '牛市', '利好', '盈利', '新高', '反弹', '增', '爆发', '升', '笑', '胜利', '逆袭', '热', '惊喜', '回暖',
                '回调', '强']
negativeWord = ['向下', '下跌', '跌', '跌停', '低迷', '顶', '顶部', '空袭', '跳水', '减仓', '减持', '卖出', '卖', '空', '清仓', '暴跌', '亏', '阴跌',
                '拖累', '利空', '考验', '新低', '跌破', '熊', '熊市', '套', '回撤', '垃圾', '哭', '退', '减', '重挫', '平仓', '破灭', '崩', '绿',
                '韭菜', '悲催', '崩溃', '下滑', '拖累', '弱']
neutralWord = ['震荡', '休养', '休养生息', '谨慎', '观望', '平稳', '过渡', '盘整']
firstPage = int(input("输入论坛起始页: "))
lastPage = int(input("输入论坛终止页："))
if lastPage < firstPage:
    print("终止页不能大于起始页")

#设置时间空间
allCount = [[0 for q in range(6)] for q in range(372)]
for monthWide in range(0,12):
    for day in range(0,31):
        allCount[day+monthWide*31][0] = monthWide+1
        allCount[day+monthWide*31][1] = day+1

#计算情绪值
print("开始计数情绪值...")
for page_num in range(firstPage, lastPage+1):
    if page_num%100 == 0:
        print("正在查询第",page_num,"页（每100页提示）...")
    url = 'http://guba.eastmoney.com/list,gssz,f_' + str(page_num) + '.html'
    request = urllib.request.urlopen(url)
    content = str(request.read(),'utf-8')
    pattern = re.compile('<span class="l3">(.*?)title="(.*?)"(.*?)<span class="l6">(\d\d)-(\d\d)</span>',re.S)
    items = re.findall(pattern,content)
    for date in range(0,372):
        for i in range(0,len(items)):
            #找到匹配时间
            if int(items[i][3]) == allCount[date][0] and int(items[i][4]) == allCount[date][1]:
                #记录当天帖子数
                allCount[date][5] +=1
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
print("情绪值如下：")
#打印输出，记录不全为0天数
nonZero = 0
for z in range(0,372):
    if (allCount[z][2])*(allCount[z][2])+(allCount[z][3])*(allCount[z][3])+(allCount[z][4])*(allCount[z][4])+(allCount[z][5])*(allCount[z][5]) !=0:
        print(allCount[z][0],"月",allCount[z][1],"日发帖总数：",allCount[z][5],"; 情绪值：[",allCount[z][2],",",allCount[z][3],",",allCount[z][4],"]")
        nonZero +=1
#生成Excel
print("生成Excel中...")
#生成有值数组
strDate = [[0 for q in range(5)] for q in range(nonZero)]
temp =0
for date in range(0,372):
    if (allCount[date][2])*(allCount[date][2])+(allCount[date][3])*(allCount[date][3])+(allCount[date][4])*(allCount[date][4])+(allCount[date][5])*(allCount[date][5]) != 0:
        i = str(allCount[date][0])
        j = str(allCount[date][1])
        l = i+'月'+j+'日'
        strDate[temp][0] = l
        strDate[temp][1] = allCount[date][5]
        strDate[temp][2] = allCount[date][2]
        strDate[temp][3] = allCount[date][3]
        strDate[temp][4] = allCount[date][4]
        temp += 1
#写入Excel
wb = xlwt.Workbook()
ws = wb.add_sheet('情绪值')
for time in range(0,nonZero):
    ws.write(time, 0 ,strDate[time][0])
    ws.write(time, 1 ,strDate[time][1])
    ws.write(time, 2, strDate[time][2])
    ws.write(time, 3, strDate[time][3])
    ws.write(time, 4, strDate[time][4])
wb.save('情绪值.xls')
print("已生成Excel.")