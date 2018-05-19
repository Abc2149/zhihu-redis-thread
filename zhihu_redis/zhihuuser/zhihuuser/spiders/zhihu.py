# -*- coding: utf-8 -*-
import scrapy,json
from zhihuuser.items import UserItem

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'

    # 用户详情url
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    # 他关注的人
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    # 关注他的人
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'


    def start_requests(self):
        yield scrapy.Request(self.user_url.format(user=self.start_user, include=self.user_query),
                             callback=self.parse_user)

        yield scrapy.Request(
            self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20),
            callback=self.parse_follows)

        yield scrapy.Request(
            self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
            callback=self.parse_followers)


    def parse_user(self, response):                # 解析用户详情信息
        result = json.loads(response.text)         # 把json数据解析为python格式的字典
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        # 请求每一个粉丝下面的关注
        yield scrapy.Request(
            self.follows_url.format(user=result.get('url_token'), include=self.follows_query, offset=0, limit=20),
            callback=self.parse_follows)

        yield scrapy.Request(
            self.followers_url.format(user=result.get('url_token'), include=self.followers_query, offset=0, limit=20),
            callback=self.parse_followers)


    def parse_follows(self, response):             # 获取粉丝关注列表
        result = json.loads(response.text)

        if 'data' in result.keys():             # 获取每个粉丝的关注列表
            for result in result.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),
                                     callback=self.parse_user)

        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(next_page,callback=self.parse_follows)

    def parse_followers(self, response):             # 获取粉丝关注列表
        result = json.loads(response.text)

        if 'data' in result.keys():             # 获取每个粉丝的关注列表
            for result in result.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),
                                     callback=self.parse_user)

        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(next_page,callback=self.parse_followers)
