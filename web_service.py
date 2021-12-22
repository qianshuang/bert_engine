# -*- coding: utf-8 -*-

import json
import shutil
import pandas as pd

from flask import Flask, jsonify
from flask import request
from gevent import pywsgi

from bert_common import *

app = Flask(__name__)


@app.route('/init_train', methods=['GET', 'POST'])
def init_train():
    """
    input json:
    {
        "data_path": "xxxxxx"  # 初始化数据存放地址，不传默认为data/all_data.txt，数据\t分隔，第0列为label，1列为content
    }

    return:
    {   'code': 0,
        'msg': 'success',
        'time_cost': 30
    }
    """
    start = datetime.datetime.now()

    if request.get_data():
        resq_data = json.loads(request.get_data())
        data_path = resq_data["data_path"].strip()
        shutil.move(data_path, DATA_FILE)

    if not os.path.exists(DATA_FILE):
        result = {'code': -1, 'msg': 'fail', 'content': 'data/all_data.txt not exist!'}
        return jsonify(result)

    # 拆分训练测试集
    df = pd.read_csv(DATA_FILE, sep='\t', dtype={'label': 'string', 'content': 'string'})
    df_test = df.sample(frac=0.1, axis=0)
    df_train = df[~df.index.isin(df_test.index)]
    df_test.to_csv(TEST_FILE, sep='\t', index=False, header=False)
    df_train.to_csv(TRAIN_FILE, sep='\t', index=False, header=False)

    # 模型训练
    train()

    res = subprocess.call(["ls", "-al"])
    if res == 0:
        print("aaaa")

    result = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start)}
    return jsonify(result)


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8088), app)
    server.serve_forever()
