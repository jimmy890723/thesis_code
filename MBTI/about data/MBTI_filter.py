import pandas as pd
import numpy as np
import re

def is_number(num):
  pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
  result = pattern.match(num)
  if result:
    return True
  else:
    if re.search('[A-Za-z]',num):
        return False
    else:
        return True

fileNameStr = './mbti_1.csv' 
DataDF = pd.read_csv(fileNameStr,encoding = "ISO-8859-1",dtype = str) #如果是中文，encoding用utf-8

gib = {'@','#','￥','%','……','&','~','—','+','*','!','$','^',"<",">",'（','）','{','}','：','“','》','《','？','|','【','】','‘','；','/','。','，','、','='}

MBTI = {'ESTJ','ESTP','ESFJ','ESFP','ENTJ','ENTP','ENFJ','ENFP','ISTJ','ISTP','ISFJ','ISFP','INTJ','INTP','INFJ','INFP'}
#1 從宏觀的角度去看數據：查看dataframe的信息
#DataDF.info()

#1.1查看每一列的数据类型    N
a = DataDF.dtypes

#1.2有多少行，多少列        N
#a = DataDF.shape

# 2.检查缺失数据
# 如果你要检查每列缺失数据的数量，使用下列代码是最快的方法。
# 可以让你更好地了解哪些列缺失的数据更多，从而确定怎么进行下一步的数据清洗和分析操作。

#a = DataDF.isnull().sum().sort_values(ascending=False)

# 3.是抽出一部分数据来，人工直观地理解数据的意义，尽可能地发现一些问题
#a = DataDF.head()
#print(a)   

for i in range(len(DataDF)):    
    #print(DataDF['posts'][i])
    str_tmp = DataDF['posts'][i]
    str_tmp = str_tmp.split('|||')
    str_save = ""
    for j in range(len(str_tmp)):
        if 'http' in str_tmp[j]:
            continue
        elif is_number(str_tmp[j]) == True:
            continue
        else:
            for ch in gib:
                if ch in str_tmp[j]:
                    #print(ch)
                    str_tmp[j] = str_tmp[j].replace(ch,"")
            #str_tmp[j] = re.sub(u"([^\u0041-\u005a])","",str_tmp[j])
            for per in MBTI:
                if per in str_tmp[j]:
                    str_tmp[j] = str_tmp[j].replace(per,"certain personality")   
            str_save += str_tmp[j]
            if j == (len(str_tmp)-1):
                break
            else:
                str_save += '|||'
    #print(str_save)
    if str_save == "":
        continue
    else:
        DataDF['posts'][i] = str_save
#print(DataDF['posts'][i])

DataDF.to_csv(f"mbti_test.csv", index=False)
# 目前濾除了URL、一些特殊自元、只有數字+空白的字串,以及直接提及的MBTI人格，但濾不掉這個 :string: