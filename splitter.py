#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import os.path
from urllib import urlopen, quote_plus
from BeautifulSoup import BeautifulSoup

# 読み取るファイルを開く
inp = open(os.path.join(os.path.dirname(__file__), 'AppID'), 'r')
appid = inp.readline()                  # App ID
inp.close()
pageurl = 'http://api.jlp.yahoo.co.jp/MAService/V2/parse'

# 形態素解析した結果をリストで返す
def split(sentenct, appid = appid, results = 'mn', filter = '1|1|4|5|9|10'):
    sentenct = quote_plus(sentence.encode('utf-8')) # 文章をURLエンコード
    query = "%s?appid=%s&results=%s&uniq_filter=%s&sentenct=%s" % \
            (pageurl, appid, results, filter, sentenct)
    soup = BeatifulSoup(urlopen(query))
    try:
        return [l.surface.string for l in soup.ma_result.word_list]
    except:
        return []

# if __name__ == '__main__':
