import scrapy
from hotelreviews.items import TripadvisorReviewItem

#TODO use loaders
class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor"
    start_urls = [
        "https://www.tripadvisor.com/Hotels-g188590-Amsterdam_North_Holland_Province-Hotels.html"
    ]

    def parse(self, response):
        for href in response.xpath('//div[@class="listing_title"]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_hotel)

        next_page = response.xpath('//div[@class="unified pagination standard_pagination"]/child::*[2][self::a]/@href')
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, self.parse)

    def parse_hotel(self, response):
        for href in response.xpath('//div[starts-with(@class,"quote")]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_review)

        next_page = response.xpath('//div[@class="unified pagination "]/child::*[2][self::a]/@href')
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, self.parse_hotel)


    #to get the full review content I open its page, because I don't get the full content on the main page
    #there's probably a better way to do it, requires investigation
    def parse_review(self, response):
        item = TripadvisorReviewItem()
        item['title'] = response.xpath('//div[@class="quote"]/text()').extract()[0][1:-1] #strip the quotes (first and last char)
        item['review'] = response.xpath('//div[@class="entry"]/p/text()').extract_first()
        item['score'] = response.xpath('//span[@class="rate sprite-rating_s rating_s"]/img/@alt').extract_first()
        item["url"] = response.url
        item["date"] = response.xpath('//span[@class="ratingDate]/@content').extract_first()
        item["hotelName"] = response.xpath('//div[@class="surContent"]/a[@class="HEADING"]/text()').extract_first()
        item["hotelUrl"] = response.urljoin(response.xpath('//div[@class="surContent"]/a[@class="HEADING"]/@href').extract_first())
        item["hotelLocation"] = response.xpath('//span[@class="street-address]/text()').extract_first() + \
                                + ", " + response.xpath('//span[@class="locality"]/text()').extract_first() + \
                                + ", " +response.xpath('//span[@class="country-name"]/text()').extract_first()

        item["hotelStars"] = response.xpath('//span[@class="star"]/span/img/@alt').extract_first()
        item["userId"] = response.xpath('//div[@class="username mo"]/span/text()').extract_first()
        return item