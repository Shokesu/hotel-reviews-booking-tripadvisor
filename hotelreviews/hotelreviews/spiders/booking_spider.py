import scrapy
from scrapy.loader import ItemLoader
from hotelreviews.items import BookingReviewItem, BookingHotelItem
import re
#crawl up to 6 pages of review per hotel
max_pages_per_hotel = 100

class BookingSpider(scrapy.Spider):
    name = "booking"
    start_urls = [
        #"http://www.booking.com/searchresults.html?aid=357026&label=gog235jc-city-XX-us-newNyork-unspec-uy-com-L%3Axu-O%3AosSx-B%3Achrome-N%3Ayes-S%3Abo-U%3Ac&sid=b9f9f1f142a364f6c36f275cfe47ee55&dcid=4&city=20088325&class_interval=1&dtdisc=0&from_popular_filter=1&hlrd=0&hyb_red=0&inac=0&label_click=undef&nflt=di%3D929%3Bdistrict%3D929%3B&nha_red=0&postcard=0&redirected_from_city=0&redirected_from_landmark=0&redirected_from_region=0&review_score_group=empty&room1=A%2CA&sb_price_type=total&score_min=0&ss_all=0&ssb=empty&sshis=0&rows=15&tfl_cwh=1",
        #add your city url here
        "https://www.booking.com/searchresults.html?city=-1364995"

    ]

    pageNumber = 1

    # def __init__(self):
        # self.items = []
        # self.hotelcount = 0
    #for every hotel
    def parse(self, response):
        # if self.hotelcount > 3000:
        #     return
        for hotelurl in response.xpath('//a[@class="hotel_name_link url"]/@href'):
            url = response.urljoin(hotelurl.extract())
            yield scrapy.Request(url, callback=self.parse_hotel)

        #
        #
        # for hotel in response.xpath('//div[@class="sr_property_block_main_row"]'):
        #     reviews = hotel.xpath('//span[@class="score_from_number_of_reviews"]/text()').extract_first() #example: 1,445 verified reviews
        #     reviews_num = ""
        #     for i in re.findall(r'\d+', reviews_num):
        #         reviews_num += i
        #     if int(reviews_num) >= 500: #when review number >= 500, then collect this hotel reviews
        #         url = response.urljoin(hotel.xpath('//a[@class="hotel_name_link url"]/@href').extract_first())
        #         yield scrapy.Request(url, callback=self.parse_hotel)
        #     else:
        #         pass
        next_page = response.xpath('//a[starts-with(@class,"paging-next")]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)

    #get its reviews page
    def parse_hotel(self, response):
        reviewsurl = response.xpath('//a[@class="show_all_reviews_btn"]/@href')
        url = response.urljoin(reviewsurl[0].extract())
        self.pageNumber = 1


        # parse web page to get basic info for each hotel

        # hotel_item = BookingHotelItem()
        # hotel_item["name"] = response.xpath('//h2[@class="hp__hotel-name"]/text()').extract_first()
        # hotel_item["url"] = response.url
        # hotel_item["score"] = response.xpath('//div[@id="js--hp-gallery-scorecard"]/a/span[@class="rating notranslate"]/span[@class="average js--hp-scorecard-scoreval"]/text()').extract_first()
        # hotel_item["location"] = response.xpath('//span[@class="hp_address_subtitle jq_tooltip"]/text()').extract_first()


        hotel_item = BookingHotelItem()
        hotel_item["name"] = response.xpath('//h2[@class="hp__hotel-name"]/text()').extract_first()
        hotel_item["score"] = response.xpath('//span[@class="average js--hp-scorecard-scoreval"]/text()').extract_first()
        hotel_item["location"] = response.xpath('//span[@class="hp_address_subtitle jq_tooltip"]/text()').extract_first()
        hotel_item["url"] = response.url
        hotel_item["reviews"] = []

        yield scrapy.Request(url, meta={"hotel_item": hotel_item}, callback=self.parse_reviews)
        # request.meta["hotel"] = hotel_item
        yield hotel_item

        # hotel_item["reviews"] = self.items
        # self.items = []

        # self.hotelcount += 1

        # yield hotel_item


        # return scrapy.Request(url, callback=self.parse_reviews)

    #and parse the reviews
    def parse_reviews(self, response):
        if self.pageNumber > max_pages_per_hotel:
            return
        # if self.pageNumber == 1:
        #     hotel = response.meta["hotel"]
        # hotel_item = response.meta['hotel_item']
        for rev in response.xpath('//div[@class="review_item_header_content_container"]/a/@href'):
            url = response.urljoin(rev.extract())
            yield scrapy.Request(url, meta={"hotel_item": response.meta["hotel_item"]}, callback= self.parse_single_review)

        # for rev in response.xpath('//li[starts-with(@class,"review_item")]'):
            # item = BookingReviewItem()
            #sometimes the title is empty because of some reason, not sure when it happens but this works
            # title = rev.xpath('.//a[@class="review_item_header_content"]/span[@itemprop="name"]/text()')
            # if title:
            #     item['title'] = title[0].extract()
            #     positive_content = rev.xpath('.//p[@class="review_pos"]//span/text()')
            #     if positive_content:
            #         item['positive_content'] = positive_content[0].extract()
            #     negative_content = rev.xpath('.//p[@class="review_neg"]//span/text()')
            #     if negative_content:
            #         item['negative_content'] = negative_content[0].extract()
            #     item['score'] = rev.xpath('.//span[@itemprop="reviewRating"]/meta[@itemprop="ratingValue"]/@content')[0].extract()
            #     #tags are separated by ;
            #     item['tags'] = ";".join(rev.xpath('.//li[@class="review_info_tag"]/text()').extract())
            # if response.meta["hotel_item"]["reviews"] == None:
            # response.meta["hotel_item"]["reviews"] = []
                # hotel_item["reviews"].append(item)
            # else:
            # response.meta["hotel_item"]["reviews"].append(dict(item))
                # self.items.append(item)

        next_page = response.xpath('//a[@id="review_next_page_link"]/@href')
        if next_page:
            self.pageNumber += 1
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_reviews)

    def parse_single_review(self, response):

        item = BookingReviewItem()
        item['title'] = response.xpath('//div[@class="review_item_header_content_container"]/div/span/text()').extract_first()
        item['score'] = response.xpath('//div[@class="review_item_review_score jq_tooltip"]/text()').extract_first()
        item['negative_content'] = response.xpath('.//p[@class="review_neg"]//span/text()').extract_first()
        item['positive_content'] = response.xpath('.//p[@class="review_pos"]//span/text()').extract_first()
        # item['tags'] =
        response.meta["reviews"].append(dict(item))
        return item