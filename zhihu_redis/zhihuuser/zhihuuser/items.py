# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field

class UserItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 名称
    name = Field()
    # 头像url
    avatar_url = Field()
    # 回答数
    answer_count = Field()
    # 文章数
    articles_count = Field()
    # 关注者
    follower_count = Field()
    # 性别 0女生 1男生
    gender = Field()
    # 签名
    headline = Field()
    # 具有唯一标识符的字段
    url_token= Field()

