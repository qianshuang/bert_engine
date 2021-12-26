# -*- coding: utf-8 -*-

import json
import shutil
import pandas as pd
import tensorflow as tf

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
        "data_path": "xxx"  # 初始化数据存放地址，不传默认为data/all_data.txt，数据\t分隔，第0列为label，1列为content
    }

    return:
    {
        'code': 0,
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
    write_lines(DATA_FILE, read_file(DATA_FILE))
    df = pd.read_csv(DATA_FILE, sep='\t', header=None)
    df_test = df.sample(frac=0.1, axis=0)
    df_train = df[~df.index.isin(df_test.index)]
    df_test.to_csv(TEST_FILE, sep='\t', index=False, header=False)
    df_train.to_csv(TRAIN_FILE, sep='\t', index=False, header=False)

    # 自动化训练 + 模型导出 + 模型加载
    all_labels = list(set(df[0].values))
    write_lines(LABEL_FILE, all_labels)
    if os.path.exists(EXPORT_DIR):
        shutil.rmtree(EXPORT_DIR)

    res_data = train(",".join(all_labels))
    if res_data == {}:
        result = {'code': -1, 'msg': 'bert train failed!', 'time_cost': time_cost(start)}
    else:
        globals()['predict_fn'] = tf.contrib.predictor.from_saved_model(get_export_dir())
        result = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start), 'data': res_data}
    return jsonify(result)


@app.route('/incre_train', methods=['GET', 'POST'])
def incre_train():
    """
    input json:
    {
        "data": "xxx"  # 训练数据，数据\t分隔，第0列为label，1列为content
    }

    return:
    {
        'code': 0,
        'msg': 'success',
        'time_cost': 30
    }
    """
    start = datetime.datetime.now()

    resq_data = json.loads(request.get_data())
    data = resq_data["data"].strip()
    append_file(TRAIN_FILE, data + "\n")

    # 自动化训练 + 模型导出 + 模型加载
    all_labels = list(set([line.strip().split("\t")[0].strip() for line in read_file(TRAIN_FILE)]))
    write_lines(LABEL_FILE, all_labels)
    if os.path.exists(EXPORT_DIR):
        shutil.rmtree(EXPORT_DIR)

    bert_eval_dict = read_bert_eval_res_to_dict(bert_eval_file)
    res_data = train(",".join(all_labels), int(bert_eval_dict["epoch"]) + 1, bert_eval_dict["eval_accuracy"])
    globals()['predict_fn'] = tf.contrib.predictor.from_saved_model(get_export_dir())

    result = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start), 'data': res_data}
    return jsonify(result)


@app.route('/classify', methods=['GET', 'POST'])
def classify():
    """
    input json:
    {
        "query": "xxx"  # 用户query
    }

    return:
    {
        'code': 0,
        'msg': 'success',
        'time_cost': 30,
        'data': {'label': 'xxx', 'score': 0.998}
    }
    """
    start = datetime.datetime.now()

    resq_data = json.loads(request.get_data())
    query = resq_data["query"].strip()

    # 模型预测
    feed_dict = {"input_ids": [], "input_mask": [], "segment_ids": []}
    input_ids, input_mask, segment_ids = convert_single_example(query.strip())
    feed_dict["input_ids"].append(input_ids)
    feed_dict["input_mask"].append(input_mask)
    feed_dict["segment_ids"].append(segment_ids)

    if "predict_fn" not in globals():
        print("reload model...")
        globals()['predict_fn'] = tf.contrib.predictor.from_saved_model(get_export_dir())
    prediction = globals()['predict_fn'](feed_dict)
    probabilities = prediction["probabilities"][0]
    label, score = get_label_score_by_probs(probabilities, read_file(LABEL_FILE))
    result = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start), 'data': {'label': label, 'score': score}}
    return jsonify(result)


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8088), app)
    server.serve_forever()
