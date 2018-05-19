import random
import os
import sys
'''
购买某代理一天永久的IP代理
'''
filename = os.path.join(os.path.dirname(sys.path[0]),'tool')
filepath = os.path.join(filename,'proxy.txt')

def get_random_proxy():
    with open(filepath, 'r')as f:
        proxies = f.readlines()
    proxy = random.choice(proxies).strip()
    return 'http://' + proxy

if __name__ =='__main__':
    get_random_proxy()
