# -*- coding: utf-8 -*-

import os

f = os.popen("ls -l")  # 返回的是一个文件对象
print(f.readlines())
