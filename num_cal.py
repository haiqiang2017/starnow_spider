#_*_  encoding:UTF-8 _*_
import os
import numpy as np
from os import listdir
from os.path import isfile, join
from six.moves import cPickle
import sys
import random
import shutil
import argparse
from getuid import get_img 
from multiprocessing import Pool

if __name__ == '__main__':
    id_list = []
    no_id_list = []
    root_path = os.path.join('/mnt/data2/start_spider',sys.argv[1])
    batchs = [
        b for b in os.listdir(root_path)
        if os.path.isdir(os.path.join(root_path, b))
    ]
    sum = 0
    for batch in batchs:
        id_list.append(batch)
    p = Pool(30)
    with open('id_list','r') as load_r:
         for id_name in load_r.readlines():
             id= id_name.split(',')[0].strip()
             if id not in id_list:
                no_id_list.append(id)
                sum += 1
    for id in no_id_list:
          p.apply_async(get_img,(id,))
    p.close()
    p.join()
    print len(set(id_list)),sum
