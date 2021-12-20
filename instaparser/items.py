# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    type = scrapy.Field()
    username = scrapy.Field()
    user_id = scrapy.Field()
    f_username = scrapy.Field()
    f_user_id = scrapy.Field()
    f_user_photo = scrapy.Field()
    # likes = scrapy.Field()
    # post_data = scrapy.Field()