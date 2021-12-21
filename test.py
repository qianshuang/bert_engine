# -*- coding: utf-8 -*-

import subprocess

a = subprocess.call(["ls", "-al"])
if a == 0:
    print("aaaa")
