# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HotelreviewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BookingReviewItem(scrapy.Item):
    title = scrapy.Field()
    score = scrapy.Field()
    positive_content = scrapy.Field()
    negative_content = scrapy.Field()
    tags = scrapy.Field()

class BookingHotelItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    location = scrapy.Field()
    score = scrapy.Field()
    reviews = scrapy.Field()

