#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import re
import math
import splitter
# import sqlite3 as sqlite
import os.path
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

def sampletrain(cl):
    dic = { \
        'Nobody owns the water' : 'good', \
        'the quick rabbit jumps fences' : 'good', \
        'buy pharmaceuticals now' : 'bad', \
        'make quick money at the online casino' : 'bad',
        'the quick brown fox jumps' : 'good' \
        }
    [cl.train(k, dic[k]) for k in dic.keys()]

def getwords(doc):
    splitter = re.compile('\\W*')
    # 単語を非アルファベットの文字で分割する
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]
    # ユニークな単語のみの集合を返す
    return dict([(w, 1) for w in words])

# def getwords(doc):
#     words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]
#     # ユニークな単語の集合を返す
#     return dict([(w, 1) for w in words])

Base = declarative_base()
class FC(Base):
    __tablename__ = 'fc'

    id = Column(Integer, primary_key = True)
    feature = Column(String)
    category = Column(String)
    count = Column(Integer)

    def __init__(self, feature, category, count):
        self.feature = feature
        self.category = category
        self.count = count

    def __repr__(self):
        return "<FC('%s', '%s', '%s')>" % (self.feature, self.category, self.count)

class CC(Base):
    __tablename__ = 'cc'

    id = Column(Integer, primary_key = True)
    category = Column(String)
    count = Column(Integer)
    fc_id = Column(Integer, ForeignKey('fc.id'))

    fc = relation(FC, backref = backref('cc', order_by = id))

    def __init__(self, category, count):
        self.category = category
        self.count = count

    def __repr__(self):
        return "<CC('%s', '%s')>" % (self.category, self.count)

class classifier:
    def __init__(self, getfeatures, filename = None):
        # 特徴 / カテゴリのカウント
        self.fc = {}
        # それぞれのカテゴリの中のドキュメント数
        self.cc = {}
        self.getfeatures = getfeatures

    # def setdb(self, dbfile):
    #     con = sqlite.connect(os.path.join(os.path.dirname(__file__), 'DATABASE/%s' % dbfile))
    #     self.cur = con.cursor()
    #     self.cur.execute('create table if not exists fc(feature, category, count)')
    #     self.cur.execute('create table if not exists cc(category, count)')

    def setdb(self, dbfile):
        url = os.path.join(os.path.dirname(__file__), 'DATABASE/%s' % dbfile)
        engine = create_engine('sqlite:///%s' % url, echo = True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind = engine)
        self.session = Session()

    # 特徴 / カテゴリのカウントを増やす
    def incf(self, f, cat):
        # self.fc.setdefault(f, {})
        # self.fc[f].setdefault(cat, 0)
        # self.fc[f][cat] += 1
        count = self.fcount(f, cat)
        if count == 0:
            # self.cur.execute("""insert into fc (feature, category, count) \
            # values (?, ?, 1)""", \
            #                  (f, cat))
            self.fc[f] = FC(f, cat, 1)
            self.session.add(self.fc[f])
        else:
            # self.cur.execute("""update fc set count = ? where feature = ? and category = ? """, \
            #                  (count + 1, f, cat))
            self.fc[f].count += 1

    # カテゴリのカウントを増やす
    def incc(self, cat):
        # self.cc.setdefault(cat, 0)
        # self.cc[cat] += 1
        count = self.catcount(cat)
        if count == 0:
            # self.cur.execute("""insert into cc (category, count) values (?, 1)""", cat)
            self.cc[cat] = CC(cat, 1)
            self.session.add(self.cc[cat])
        else:
            # self.cur.execute("""update cc set count = ? where category = ?""", \
            #                  (count + 1, cat))
            self.cc[cat].count += 1

    # あるカテゴリの中に特徴が現れた数
    def fcount(self, f, cat):
        # if f in self.fc and cat in self.fc[f]:
        #     return float(self.fc[f][cat])
        # else:
        #     return 0.0
        # res = self.cur.execute("""select count from fc where feature = ? and category = ?""", \
        #                        (f, cat)).fetchone()

        res = self.session.query(FC).filter(FC.feature == f).filter(FC.category == cat).first()
        
        if res == None:
            return 0
        else:
            return res.count

    # あるカテゴリの中のアイテムたちの数
    def catcount(self, cat):
        # if cat in self.cc:
        #     return float(self.cc[cat])
        # else:
        #     return 0

        # res = self.cur.execute("""select count from cc where category = ?""", \
        #                        (cat)).fetchone()
        
        res = self.session.query(CC).filter(CC.category == cat).first()
        
        if res == None:
            return 0
        else:
            return res.count

    # アイテムたちの総数
    def totalcount(self):
        return sum(self.cc.values())

    # すべてのカテゴリたちのリスト
    def categories(self):
        # return self.cc.keys()
        # cur = self.cur.execute("""select category from cc""")
        cur = self.session.query(CC.category)
        # return [d[0] for d in cur]
        return cur

    def totalcount(self):
        # res = self.cur.execute("""select sum(count) from cc""").fetchone()
        res = self.session.query(func.sum(CC.count)).first()
        if res == None:
            return 0
        else:
            return res[0]

    def train(self, item, cat):
        features = self.getfeatures(item)
        # このカテゴリ中の特徴たちのカウントを増やす
        # for f in features:
        #     self.incf(f, cat)
        [self.incf(f, cat) for f in features]
        # このカテゴリのカウントを増やす
        self.incc(cat)
        self.session.commit()

    def fprob(self, f, cat):
        if self.catcount(cat) == 0:
            return 0
        else:
            return self.fcount(f, cat) / self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight = 1.0, ap = 0.5):
        # 現在の確率を計算する
        basicprob = prf(f, cat)

        # この特徴がすべてのカテゴリ中に出現する数を数える
        totals = sum([self.fcount(f, c) for c in self.categories()])

        # 重み付けした平均を計算
        return ((weight * ap) + (totals * basicprob)) / (weight + totals)

class naivebayes(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self, getfeatures)
        self.thresholds = {}

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds:
            return 1.0
        else:
            return self.thresholds[cat]
    
    def docprob(self, item, cat):
        features = self.getfeatures(item)
        # すべての特徴の確率を掛け合わせる
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount()
        docprob = self.docprob(item, cat)
        return docprob * catprob

    def classify(self, item, default = None):
        probs = {}
        # もっとも確率の高いカテゴリを探す
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # 確率がしきい値 * 2番目にベストなものを超えているか確認する
        for cat in probs:
            if cat == best:
                continue
            elif probs[cat] * self.getthreshold(best) > probs[best]:
                return default
            else:
                return best
            
class fisherclassifier(classifier):

    def __init__(self, getfeatures):
        classifier.__init__(self, getfeatures)
        self.minimums = {}

    def setminimum(self, cat, min):
        self.minimums[cat] = min

    def getminimum(self, cat):
        if cat not in self.minimums:
            return 0
        else:
            return self.minimums[cat]
            
    def cprob(self, f, cat):
        # このカテゴリの中でのこの特徴の頻度
        clf = self.fprob(f, cat)
        if clf == 0:
            return 0
        # すべてのカテゴリ中でのこの特徴の頻度
        freqsum = sum([self.fprob(f, c) for c in self.categories()])
        # 確率はこのカテゴリでの頻度を全体の頻度で割ったもの
        return clf / freqsum

    def fisherprob(self, item, cat):
        # すべての確率を掛け合わせる
        p = 1
        features = self.getfeatures(item)
        for f in features:
            p *= self.weightedprob(f, cat, self.cprob)
        # 自然対数をとり-2を掛け合わせる
        fscore = -2 * math.log(p)
        # 関数chi2の逆数を利用して確率を得る
        return self.invchi2(fscore, len(features) * 2)

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df//2):
            term *= m / i
            sum += term
        return min(sum, 1.0)

    def classify(self, item, default = None):
        # もっともよい結果を探してループする
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherprob(item, c)
            # 下限値を超えていることを確認する
            if p > self.getminimum(c) and p > max:
                best = c
                max = p
        return best
    
if __name__ == '__main__':
    cl = fisherclassifier(getwords)
    cl.setdb('test1.db')
    sampletrain(cl)
    cl2 = naivebayes(getwords)
    cl2.setdb('test1.db')
    print cl2.classify('quick money')
