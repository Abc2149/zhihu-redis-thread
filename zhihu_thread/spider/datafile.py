'''
- 将知乎用户的个人信息json存储到csv文件中。
- 实现了一些必要的功能：
    - 从已有的csv文件中提取出所有用户，用于程序中断后重启时加载已爬取用户列表。
    - 从已有的csv文件中提取指定数目的未爬取用户，用于程序中断后重启时生成任务队列。
- 类DataFile为单例模式，在程序中只有一个实例。
- 线程安全。
'''

import threading
import os
import sys
import csv
import codecs
import json

# 操作文件csv使用互斥锁，用户保证线程安全
FILELOCK = threading.Lock()


class Singleton(object):
    """
    实现单例模式，DataFile在程序中只有一个实例
    """
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)
        return cls._instance


class DataFile(Singleton):
    def __init__(self):
        # 存储数据文件夹的绝对路径
        self.FILEPATH = os.path.join(os.path.dirname(sys.path[0]), 'datafile')
        # 每个文件的文件名后缀
        self.SUFFIX = '.csv'
        # 每个文件的文件大小
        self.MAXSIZE = 100 * 1024 * 1024
        # 每个文件的表头，第一行的内容，方便使用csv库中的DictWrite/DictReader按dict方式处理数据
        self.TABLEHEADER = ['user_url_token', 'user_detail', 'user_following_list']
        # 由于数据量较大，分对个文件存储，通过变量指向当前操做的文件
        self.__currentfile = ''
        # 更新当前操作的文件，每个文件不超过100MB，所有需要不断检查已有文件的大小，当大小超过限制，就创建
        # 一个新文件，并更新__currentfile变量的文件名
        self.file_tag = 1

    def loadusercrawled(self):
        # 加载已爬取的用户
        # 数据文件夹不存在，返回一个空列表
        if not os.path.exists(self.FILEPATH):
            return list()

        FILELOCK.acquire()
        # 找出所有文件夹中的csv文件，存储在列表中
        csvfilelist = list()
        for filename in os.listdir(self.FILEPATH):  # 打开文件，返回路径下的文件和文件列表
            filename = os.path.join(self.FILEPATH, filename)  # 组合当前文件的路径
            if os.path.splitext(filename)[1] == self.SUFFIX:  # 分离文件名与扩展名
                with open(filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)  # 字典类型，表格的表头为key,每行为value,value有几行就有几个字典数据
                    if reader.fieldnames == self.TABLEHEADER:  # 判断表头['user_url_token','user_detail','user_following_list']
                        csvfilelist.append(os.path.join(self.FILEPATH, filename))  # 符合内容的csv文件存储在一个列表中

        # 从上面的列表中，依次遍历每个文件，得到一个包含已经爬取用户的url_token的列表
        usercrawled = list()
        for filename in csvfilelist:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    usercrawled.append(row[self.TABLEHEADER[0]])  # 第一列为已爬取的用户

        FILELOCK.release()
        return usercrawled

    def loaduseruncrawled(self, usercrawled_set, user_count=100000):
        '''
        从已有的文件中加载第三列已经爬取的用户关注列表 
        去重以爬取得用户，得到一个未爬取的用户列表
        默认加载100000个未爬取的用户
        :param usercrawled_set: 
        :param user_count: 
        :return: 
        '''

        if not os.path.exists(self.FILEPATH):  # 文件不存在
            useruncrawled = list()
            useruncrawled.append('excited-vczh')  # 手动添加一个未爬取用户
            return useruncrawled

        FILELOCK.acquire()
        # 找出所有文件夹中的csv文件，存储在列表中
        csvfilelist = list()
        for filename in os.listdir(self.FILEPATH):  # 打开文件，返回路径下的文件和文件列表
            filename = os.path.join(self.FILEPATH, filename)  # 组合当前文件的路径
            if os.path.splitext(filename)[1] == self.SUFFIX:  # 分离文件名与扩展名
                with open(filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)  # 字典类型，表格的表头为key,每行为value,value有几行就有几个字典数据
                    if reader.fieldnames == self.TABLEHEADER:  # 判断表头['user_url_token','user_detail','user_following_list']
                        csvfilelist.append(os.path.join(self.FILEPATH, filename))
        # csvfilelist.sort()

        # 未爬取列表
        useruncrawled = list()
        for filename in csvfilelist:  # 循环所有的文件列表
            if len(useruncrawled) >= user_count:  # 未爬取的列表中已有100000个待爬取用户
                break
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                user_following_list = list()  # 关注列表用户，用于对比去重一些爬取过的用户
                for row in reader:
                    data = row[self.TABLEHEADER[2]]   # 全部的列值
                    data_dict = json.loads(data)['id']
                    user_following_list+=data_dict  # 原数据存储为列表
                for user in user_following_list:
                    if len(useruncrawled) >= user_count:
                        break
                    if user not in usercrawled_set:  # 用户不在已爬取的列表中
                        useruncrawled.append(user)  # 添加到未爬取的列表
        FILELOCK.release()

        if len(useruncrawled) == 0:
            useruncrawled.append('excited-vczh')
        return useruncrawled


    def __getcurrentfile(self):
        '''
        获取当前文件操作
        当文件不存在和文件大小超过限制，建立新文件。
        :return: 文件绝对路径
        '''
        FILELOCK.acquire()
        while True:
            self.suffix = str(self.file_tag) + self.SUFFIX
            filename = os.path.join(self.FILEPATH, self.suffix)
            if os.path.exists(filename):
                if os.path.exists(filename) and os.path.getsize(filename) < self.MAXSIZE:
                    self.__currentfile = filename
                    break
                else:
                    self.file_tag += 1
            else:
                self.suffix = str(self.file_tag) + self.SUFFIX
                filename = os.path.join(self.FILEPATH, self.suffix)
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    headerrow = dict()
                    for x in self.TABLEHEADER:
                        headerrow[x] = x
                    writer = csv.DictWriter(csvfile, self.TABLEHEADER)
                    writer.writerow(headerrow)
                    self.__currentfile = filename
                    break
        FILELOCK.release()
        return self.__currentfile

    def saveinfo(self, userinfo):
        """
        存入用户信息。
        """
        filename = self.__getcurrentfile()
        FILELOCK.acquire()
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                # csvfile.write(codecs.BOM_UTF8)
                writer = csv.DictWriter(csvfile, self.TABLEHEADER)
                writer.writerow(userinfo)
                # 批量存入数据
                #for userinfo in userinfolist:
                    #writer.writerow(userinfo)
        except:
            pass
        FILELOCK.release()
        return None

if __name__ == '__main__':
    pass


















