#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

def docclass_test():
    cl = fisherclassifier(getwords)
    cl.setdb('test1.db')
    sampletrain(cl)
    cl2 = naivebayes(getwords)
    cl2.setdb('test1.db')
    cl2.classify('quick money')

if __name__ == '__main__':
    import nose
    nose.main()
