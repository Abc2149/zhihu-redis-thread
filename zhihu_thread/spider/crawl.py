'''
Description:
    获取指定用户的详情信息和该用户关注的用户列表
    类crawl为单例模式，在一个程序中只有一个实例。创建Crawl类将获取的用户信息存放在一个字典中并返回，在程序运行
    期间，多线程会创建多个Crawl对象的实例，这就导致系统中存在多个Crawl的实例对象，浪费内存资源，所以在程序运行之间只
    允许一个实例对象的存在
    在python中，可以使用多种方法实现单列模式。
    在这里使用__new__
    当我们实例化一个对象时，是先执行了类的__new__方法实例化对象，然后在执行类的__init__方法，对对象进行
    初始化，所以基于这个，实现单例模式。
    测试：线程安全 
'''
import json

import requests
from fake_useragent import UserAgent
from tool import proxy
ua = UserAgent()

headers = {
    'user-agent': ua.random,
    'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'  # 未登录状态授权码
}


class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class Crawl(Singleton):
    '''
    获取指定用户的详情信息和该用户关注的用户列表
    '''
    def __init__(self):
        self.following_list = list()            # 存储粉丝列表

    def __getdetail(self, url_token):  # 定义类的私有方法，不能在类的外部调用
        '''
        获取用户详情信息
        :param url_token: 
        :return: 包含用户详情的dict()
        '''
        # 用户详情url
        user_url = 'https://www.zhihu.com/api/v4/members/{url_token}?include={include}'
        user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
        url = user_url.format(url_token=url_token, include=user_query)
        try:
            response = requests.get(url, headers=headers)  # proxies= proxy.get_random_proxy()
            if response.status_code == 200:
                self.page_json = json.loads(response.text)
            else:
                # print(response.status_code)    # 知乎已重置用户，请求返回401
                self.page_json=dict()
        except:
            self.page_json = dict()
        return self.page_json

    def __requestinfo(self, url):
        '''
        :param url: 用户粉丝地址
        :return: 粉丝列表
        '''
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            items = json.loads(response.text)
            for item in items['data']:
                self.following_list.append(item['url_token'])
            # 爬取他所有关注的人
            if items['paging']['is_end'] == False:
                next_page = items['paging']['next']
                # print(self.url_token,len(self.following_list))
                self.__requestinfo(next_page)
        return self.following_list

    def getinfo(self, url_token):
        '''
        :param url_token:  指定的用户url
        :return: 用户详情，用户粉丝，具有用户标识的url_token
        '''
        self.url_token = url_token
        user_detail = self.__getdetail(url_token)
        # 获取他关注的用户列表
        user_following_url = 'https://www.zhihu.com/api/v4/members/{url_token}/followees?include={include}&offset={offset}&limit={limit}'
        user_following_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
        url = user_following_url.format(url_token=url_token, include=user_following_query, offset=0, limit=20)
        try:
            following_list = json.dumps({'id':self.__requestinfo(url)})  # 获取用户关注的列表
            self.following_list=[]
        except:
            following_list=''

        info = {
            'user_url_token': url_token,
            'user_detail': json.dumps(user_detail, ensure_ascii=False),
            'user_following_list': following_list,
        }
        # print(info['user_detail'])
        # print(info)
        # data = json.loads(info['user_following_list'])['id']
        # print(self.url_token,'关注了',len(data))
        return info

if __name__ == '__main__':
    crawl = Crawl()
    crawl.getinfo('excited-vczh')
    # 测试线程安全，以及请求数据是否正确
    # import threading
    # def task():
    #     obj = Crawl()
    #     print(obj)
    #     obj.getinfo('excited-vczh')
    # for i in range(2):
    #     t = threading.Thread(target=task,)
    #     t.start()










