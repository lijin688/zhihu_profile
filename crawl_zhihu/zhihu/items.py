# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuFolloweeItem(scrapy.Item):
    user_name = scrapy.Field()
    sex  = scrapy.Field()
    user_sign = scrapy.Field()
    user_url = scrapy.Field()
    user_avatar = scrapy.Field()
    user_address = scrapy.Field()


class ZhihuDynamicItem(scrapy.Item):
    user_token = scrapy.Field()
    answer_create = scrapy.Field()
    # user_sign = scrapy.Field()
    # user_url = scrapy.Field()
    # user_avatar = scrapy.Field()
    # user_add = scrapy.Field()