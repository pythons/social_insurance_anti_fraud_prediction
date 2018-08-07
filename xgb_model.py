# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     lgb_model
   Description :
   Author :       Administrator
   date：          2018/7/12 0012
-------------------------------------------------
   Change Activity:
                   2018/7/12 0012:
-------------------------------------------------
"""
__author__ = 'Administrator'
import time
import pandas as pd
import numpy as np
import time
from sklearn.cross_validation import KFold
import lightgbm as lgb
from feature_integrate.feature_integrate import *
seed=1024
np.random.seed(seed)
time_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

train_path = 'data/feature/train/'
test_path = 'data/feature/test/'

# train = pd.read_csv(train_path + 'train.csv')
# test = pd.read_csv(test_path + 'test.csv')
train = train_set()
test = test_set()

print('the number of feature: ' + str(train.shape[1]))
print('the column of feature: ' + train.columns)

train_userid = train.pop('PERSONID')
train_y = pd.read_csv('data/train_id.csv',sep='\t')['LABEL']
col = train.columns
train_x = train[col].values
test_userid = test.pop('PERSONID')

params = {
    'boosting_type': 'gbdt',
    'objective': 'binary',
    'metric': {'auc', 'binary_logloss'},
    'num_leaves': 32,
    'learning_rate': 0.02,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': 0,
    'scale_pos_weight': 2
}
n_fold = 5
# kf = KFold(n=train_the1owl.shape[0], n_folds=n_fold, shuffle=True, random_state=2017)
kf = KFold(n=train.shape[0], n_folds=n_fold, shuffle=True, random_state=2017)

n = 0
for index_train, index_eval in kf:

    x_train, x_eval = train.iloc[index_train], train.iloc[index_eval]
    y_train, y_eval = train_y[index_train], train_y[index_eval]

    lgb_train = lgb.Dataset(x_train, y_train)
    lgb_eval = lgb.Dataset(x_eval, y_eval, reference=lgb_train)

    # gbm = lgb.train(params,
    #                 lgb_train,
    #                 num_boost_round=50000,
    #                 valid_sets=[lgb_eval],
    #                 verbose_eval=100,
    #                 early_stopping_rounds=500)
    gbm = lgb.train(params,
                    lgb_train, # 训练集
                    valid_sets=lgb_eval,  # 验证集
                    num_boost_round=40000, # 迭代次数 40000 -> 10000
                    verbose_eval=250, # 每隔250次，打印日志
                    early_stopping_rounds=500)

    print('start predicting on test...')
    testpreds = gbm.predict(test.values)
    if n > 0:
        totalpreds = totalpreds + testpreds
    else:
        totalpreds = testpreds
    # gbm.save_model('lgb_model_fold_{}.txt'.format(n), num_iteration=gbm.best_iteration)
    n += 1

totalpreds = totalpreds / n

# submit result
res = pd.DataFrame()
res['PERSONID'] = list(test_userid.values)
res['Pre'] = totalpreds
res.to_csv('data/submit/xgb_%s.csv'%str(time_date), index=False, sep='\t')