import scrapy

from ..items import BookDetailItems


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    custom_settings = {"FEEDS": {"booksData.csv": {"format": "csv"}}}

    def parse(self, response):
        """
        Extracts the data from the website.
        """
        books = response.css("article.product_pod")

        for book in books:
            book_detail_page = book.css("h3 a::attr(href)").get()
            book_detail_url = (
                f"https://books.toscrape.com/{book_detail_page}"
                if "catalogue/" in book_detail_page
                else f"https://books.toscrape.com/catalogue/{book_detail_page}"
            )
            yield response.follow(book_detail_url, callback=self.parse_book_detail)
            # yield {
            #     "book_title": book.css("h3 a::text").get(),
            #     "book_price": book.css("div.product_price p.price_color::text").get(),
            #     "book_url": book.css("h3 a::attr(href)").get(),
            # }

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            next_page_url = (
                f"https://books.toscrape.com/{next_page}"
                if "catalogue/" in next_page
                else f"https://books.toscrape.com/catalogue/{next_page}"
            )
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_detail(self, response):
        """
        Extracts the page response of an Detail page.
        """
        book_details = BookDetailItems()
        book_details["book_title"] = response.css("h1::text").get()
        book_details["book_category"] = response.xpath(
            "//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()"
        ).get()
        book_details["book_price"] = response.css("p.price_color::text").get()
        book_details["book_url"] = response.url
        book_details["book_description"] = response.xpath(
            "//div[@id='product_description']/following-sibling::p/text()"
        ).get()
        book_details["book_rating"] = response.css("p.star-rating::attr(class)").get()
        table = response.css("table tr")
        book_details["product_type"] = table[1].css("td::text").get()
        book_details["price_excluded_tax"] = table[2].css("td::text").get()
        book_details["price_included_tax"] = table[3].css("td::text").get()
        book_details["tax"] = table[4].css("td::text").get()
        book_details["availability"] = table[5].css("td::text").get()
        book_details["number_of_reviews"] = table[6].css("td::text").get()

        yield book_details
