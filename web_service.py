# -*- coding: utf-8 -*-

import json

from flask import Flask, jsonify
from flask import request
from gevent import pywsgi
from common import *

app = Flask(__name__)


@app.route('/init_train', methods=['GET', 'POST'])
def init_train():
    """
    input json:
    {
        "data_path": "xxxxxx"  # 初始化数据存放地址
    }

    return:
    {   'code': 0,
        'msg': 'success',
        'time_cost': 30
    }
    """
    start = datetime.datetime.now()
    if not request.get_data() or request.get_data() == "":
        data_path = "data/all_data.txt"
    else:
        resq_data = json.loads(request.get_data())
        data_path = resq_data["data_path"].strip()

    result = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start)}
    return jsonify(result)


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 8088), app)
    server.serve_forever()
