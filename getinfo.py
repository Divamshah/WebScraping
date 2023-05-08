import scrapy
from scrapy import Request

class GetinfoSpider(scrapy.Spider):
    name = 'getinfo'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']
    
    #Parse information from a single page. 
    def parse(self, response):
        books = response.xpath('//article[@class="product_pod"]')
        for book in books:
            title = book.xpath('h3/a/@title').extract_first()
            price = book.xpath('div[@class="product_price"]/p[@class ="price_color"]/text()').extract_first()[1:]
            star = book.xpath('p/@class').extract_first().split()[-1]
            rel_url = book.xpath('h3/a/@href').extract_first()
            abs_url = response.urljoin(rel_url)
            # Requesting to collect information from inner layer of the page and passing it down the parse-page function. 
            yield Request(abs_url, callback = self.parse_page, dont_filter = True,
                          meta = {'Title' : title, 'Price' : price, 'Star' : star, 'URL' : abs_url })
        
        # Visit the next page and call parse function to repeat the scraping. 
        rel_next_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        abs_next_url = response.urljoin(rel_next_url)    
        yield Request(abs_next_url, callback = self.parse)
    
    #Parse information from next layer of the page. (Inner Layer).
    def parse_page(self, response):
        #Takes existing information from the meta var, that is collected in the parse function. 
        title = response.meta.get('Title')
        price = response.meta.get('Price')
        star = response.meta.get('Star')
        url = response.meta.get('URL')
        #Collecting information from the inner layer and then appending it together. 
        availability = response.xpath('//p[@class="instock availability"]/text()').extract()[1].strip()
        description = response.xpath('//article[@class="product_page"]/p/text()').extract_first()
        yield {'Title' : title, 'Price' : price, 'Star' : star, 'URL' : url, 'Availability' : availability, 'Description' : description}