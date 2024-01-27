# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookscrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BookDetailItems(scrapy.Item):
    """
    Defines the structure for handling the details of a Book.
    """

    book_title = scrapy.Field()
    book_category = scrapy.Field()
    book_price = scrapy.Field()
    book_url = scrapy.Field()
    book_description = scrapy.Field()
    book_rating = scrapy.Field()
    product_type = scrapy.Field()
    price_excluded_tax = scrapy.Field()
    price_included_tax = scrapy.Field()
    tax = scrapy.Field()
    availability = scrapy.Field()
    number_of_reviews = scrapy.Field()
