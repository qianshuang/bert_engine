# -*- coding: utf-8 -*-

import datetime


def main():
    import time
    time.sleep(7)


start_time = datetime.datetime.now()
main()
end_time = datetime.datetime.now()
time_cost = end_time - start_time
print(time_cost)
print(str(time_cost).split('.')[0])
