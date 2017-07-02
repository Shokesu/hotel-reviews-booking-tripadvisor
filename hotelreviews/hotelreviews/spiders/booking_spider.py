from __future__ import absolute_import
import scrapy
from scrapy.loader import ItemLoader
from hotelreviews.items import BookingReviewItem, BookingHotelItem


import re
#crawl up to 6 pages of review per hotel
max_pages_per_hotel = 100

class BookingSpider(scrapy.Spider):
    name = "booking"
    start_urls = [
        "https://www.booking.com/searchresults.html?city=-1364995"
    ]

    pageNumber = 1

    def parse(self, response):
        # if self.hotelcount > 3000:
        #     return
        for hotelurl in response.xpath('//a[@class="hotel_name_link url"]/@href'):
            url = response.urljoin(hotelurl.extract())
            yield scrapy.Request(url, callback=self.parse_hotel)

        next_page = response.xpath('//a[starts-with(@class,"paging-next")]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)

    #get its reviews page
    def parse_hotel(self, response):
        reviewsurl = response.xpath('//a[@class="show_all_reviews_btn"]/@href')
        url = response.urljoin(reviewsurl.extract_first())
        self.pageNumber = 1

        hotel_item = BookingHotelItem()
        hotel_item["name"] = response.xpath('//h2[@class="hp__hotel-name"]/text()').extract_first()
        hotel_item["score"] = response.xpath('//span[@class="average js--hp-scorecard-scoreval"]/text()').extract_first()
        hotel_item["location"] = response.xpath('//span[@class="hp_address_subtitle jq_tooltip"]/text()').extract_first()
        hotel_item["url"] = response.url
        hotel_item["reviews"] = []

        request = scrapy.Request(url, callback=self.parse_reviews)
        request.meta["hotel_item"] = hotel_item


        # request.meta["hotel"] = hotel_item
        yield request

        # hotel_item["reviews"] = self.items
        # self.items = []

        # self.hotelcount += 1

        # yield hotel_item


        # return scrapy.Request(url, callback=self.parse_reviews)

    #and parse the reviews
    def parse_reviews(self, response):
        # if self.pageNumber > max_pages_per_hotel:
        #     return
        # if self.pageNumber == 1:
        #     hotel = response.meta["hotel"]
        # hotel_item = response.meta['hotel_item']
        reviews_generator = response.xpath('//div[@class="review_item_header_content_container"]/a/@href').extract()
        for rev in response.xpath('//div[@class="review_item_header_content_container"]/a/@href').extract():
            url = response.urljoin(rev)
            yield scrapy.Request(url, meta={"hotel_item": response.meta["hotel_item"]}, callback= self.parse_single_review)
            # request.meta["hotel_item"] = response.meta["hotel_item"]
            #  request

        next_page = response.xpath('//a[@id="review_next_page_link"]/@href')
        if next_page:
            self.pageNumber += 1
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_reviews)

    def parse_single_review(self, response):

        hotel_item = response.meta["hotel_item"]


        item = BookingReviewItem()
        item['title'] = response.xpath('//div[@class="review_item_header_content_container"]/div/span/text()').extract_first()
        item['score'] = response.xpath('//div[@class="review_item_review_score jq_tooltip"]/text()').extract_first()
        item['negative_content'] = response.xpath('.//p[@class="review_neg"]//span/text()').extract_first()
        item['positive_content'] = response.xpath('.//p[@class="review_pos"]//span/text()').extract_first()
        item['date'] = response.xpath('.//p[@class="review_item_date"]/text()').extract_first()
        # item['tags'] =
        hotel_item["reviews"].append(dict(item))
        yield hotel_item