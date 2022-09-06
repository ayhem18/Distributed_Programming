import MyClient as c
import os
import time

time.sleep(1.5)
file = os.path.join("test_files", 't2.txt')
c.trans_file(8888, file, "f2.txt")
