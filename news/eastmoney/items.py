# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EastmoneyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class News(scrapy.Item):
    publish_time = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()


class Comment(scrapy.Item):
    publish_time = scrapy.Field()
    device = scrapy.Field()
    text = scrapy.Field()
    score = scrapy.Field()
    title = scrapy.Field(serializer=str)
    total_score = scrapy.Field(serializer=str)
    download_time = scrapy.Field(serializer=str)