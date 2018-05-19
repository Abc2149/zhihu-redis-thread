'''
    多线程
    主线程：维护一个待爬取响应队列，更新待爬取和已爬取数量
    子线程：从响应队列获取用户，保存用户信息，获取新的用户，放入任务队列

'''

from queue import Queue
from threading import Thread
from datafile import DataFile
from crawl import Crawl
import sys
import os
import time
import json

# 任务队列，从主线程到工作线程
task_queue = Queue(maxsize=100000)

# 响应队列，从工作线程到主线程
response_queue = Queue()

# 数据存储
data_file = DataFile()

# 用户信息获取
crawl = Crawl()

# 工作线程数量
threads_num = 100


class MasterThread(Thread):
    def __init__(self):
        super(MasterThread, self).__init__()

        self.count = {
            'crawled_count': 0,   # 已爬用户数量
            'task_count': 0,      # 任务数量
        }
        # 从本地文件加载上次中断已爬取的用户
        crawled_list = data_file.loadusercrawled()
        self.crawled_set = set(crawled_list)
        print('加载上次中断已爬取的用户', len(self.crawled_set))
        # 从本地加载上次中断未爬取的用户
        tocrawled_list = data_file.loaduseruncrawled(self.crawled_set)  # 未爬取的用户列表
        print('加载上次中断未爬取的用户',len(tocrawled_list))
        # 未爬取用户集合
        self.task_set = set()
        for token in tocrawled_list:
            try:                              # 默认设置队列中数量为10万个
                task_queue.put_nowait(token)  # 无阻塞的向队列添加任务，队列为满时，不等待，直接抛出异常
                self.task_set.add(token)
            except:
                continue
        self.count['crawled_count'] = len(crawled_list)  # 统计上次已爬取用户数量
        self.count['task_count'] = len(self.task_set)    # 统计上次未爬取用户数量

    def run(self):
        while self.count['crawled_count'] < 100000:  # 默认爬取用户数量10W
            responseitem = response_queue.get()  # 响应队列获得数据
            # 确认是否爬取到一个用户信息，则加入已爬取的集合中
            if responseitem['state'] == 'OK':
                self.crawled_set.add(responseitem['user_url_token'])
                # 更新已爬取状态新信息
                self.count['crawled_count'] += 1
            # 成功爬取，从待爬取集合中删除
            if responseitem['user_url_token'] in self.task_set:
                self.task_set.remove(responseitem['user_url_token'])

            # 获得他关注的用户列表
            followinglist = responseitem['user_following_list']
            for token in followinglist:
                if token not in self.crawled_set and token not in self.task_set:
                    try:
                        task_queue.put_nowait(token)
                        # 更新未爬取用户集合信息
                        self.task_set.add(token)
                    except:
                        continue
                        # 更新状态
                    self.count['task_count'] = len(self.task_set)
            # 输出状态信息
            self.log()
        print("Master thread exited.")

    def log(self):
        sys.stdout.write('已爬取用户'+str(self.count['crawled_count'])+'---未爬取用户'+str(self.count['task_count'])+ '\r')
        sys.stdout.flush()


class WorkerThread(Thread):
    def __init__(self):
        super(WorkerThread, self).__init__()

    def run(self):
        while True:
            try:
                # 从任务队列获取一个url_token
                token = task_queue.get(block=True, timeout=30)
            except:
                break
            # 获取该用户的信息和他关注的用户
            info = crawl.getinfo(token)
            # 生成响应队列信息
            responseitem = {'user_url_token': info['user_url_token'],
                            'user_following_list': json.loads(info['user_following_list'])['id']
                            }
            # 保存用户信息
            data_file.saveinfo(info)
            responseitem['state'] = 'OK'
            # 响应队列中添加信息
            response_queue.put(responseitem)
        print("Worker thread exited.")


if __name__ == '__main__':
    master_thread = MasterThread()

    worker_list = []
    for i in range(threads_num):
        worker_thread = WorkerThread()
        worker_list.append(worker_thread)

    master_thread.start()
    for t in worker_list:
        t.start()

    master_thread.join()
    for t in worker_list:
        t.join()




