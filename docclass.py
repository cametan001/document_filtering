#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import re
import math
import splitter

# def getwords(doc):
#     splitter = re.compile('\\W*')
#     # 単語を非アルファベットの文字で分割する
#     words = [s.lower() for s in splitter.split(doc)
#              if len(s) > 2 and len(s) < 20]
#     # ユニークな単語のみの集合を返す
#     return dict([(w, 1) for w in words])

def getwords(doc):
    words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]
    # ユニークな単語の集合を返す
    return dict([(w, 1) for w in words])

class classifier:
    def __init__(self, getfeatures, filename = None):
        # 特徴 / カテゴリのカウント
        self.fc = {}
        # それぞれのカテゴリの中のドキュメント数
        self.cc = {}
        self.getfeatures = getfeatures

    # 特徴 / カテゴリのカウントを増やす
    def incf(self, f, cat):
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    # カテゴリのカウントを増やす
    def incc(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    # あるカテゴリの中に特徴が現れた数
    def fcount(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    # あるカテゴリの中のアイテムたちの数
    def catcount(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    # アイテムたちの総数
    def totalcount(self):
        return sum(self.cc.values())

    # すべてのカテゴリたちのリスト
    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.getfeatures(item)
        # 

# if __name__ == '__main__':
