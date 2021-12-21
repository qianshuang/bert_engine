# -*- coding: utf-8 -*-

import datetime


def open_file(filename, mode='r'):
    return open(filename, mode, encoding='utf-8', errors='ignore')


def read_file(filename):
    return [line.strip() for line in open(filename).readlines()]


def write_file(filename, content):
    open_file(filename, mode="w").write(content)


def write_lines(filename, list_res):
    test_w = open_file(filename, mode="w")
    for j in list_res:
        test_w.write(j + "\n")


def time_cost(start):
    end_time = datetime.datetime.now()
    return str(end_time - start).split('.')[0]
