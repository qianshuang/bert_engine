# -*- coding: utf-8 -*-

import sys
import os

from common import *

DATA_FILE = "data/all_data.txt"
TRAIN_FILE = "data/train.txt"
TEST_FILE = "data/test.txt"


def build_bert_cmd(num_train_epochs=1):
    cmd = ["python3", "bert/run_classifier.py",
           "--data_dir=./data",
           "--bert_config_file=bert/uncased_L-12_H-768_A-12/bert_config.json",
           "--task_name=comm100",
           "--vocab_file=bert/uncased_L-12_H-768_A-12/vocab.txt",
           "--output_dir=bert/output",
           "--init_checkpoint=bert/uncased_L-12_H-768_A-12/bert_model.ckpt",
           "--do_train=True",
           "--do_eval=True",
           "--num_train_epochs=" + str(num_train_epochs)]
    return " ".join(cmd)


def train():
    for epoch in range(1, sys.maxsize):
        cmd = build_bert_cmd(epoch)
        f = os.popen(cmd)
        print(f.readlines())
