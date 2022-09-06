import MyClient as c
import os
import time


file = os.path.join("test_files", 't3.txt')
c.trans_file(8888, file, "f3.txt")
