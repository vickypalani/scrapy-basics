# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os

import psycopg2
from dotenv import load_dotenv

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

load_dotenv()


class BookscrapperPipeline:
    """
    Cleans the BookDetailItem model
    """

    def process_item(self, item, spider):
        """
        Transforms the book detail item
        """
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        for field in field_names:
            if field != "description":
                adapter[field] = (
                    adapter.get(field).strip()
                    if field != "availability"
                    else adapter.get(field).split("(")[1].split(" ")[0].strip()
                )

        field_related_to_price = [
            "price_excluded_tax",
            "price_included_tax",
            "tax",
            "book_price",
        ]
        for field in field_related_to_price:
            adapter[field] = float(adapter.get(field).replace("£", ""))

        rating_mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        adapter["book_rating"] = rating_mapping.get(
            adapter.get("book_rating").split(" ")[1], 0
        )

        return item


class StoreBookDetailsPipeline:
    """
    Stores the BookDetailItem inside a PostgreSQL database
    """

    def __init__(self):
        self.con = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cursor = self.con.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS book_details (
                id SERIAL PRIMARY KEY,
                book_title VARCHAR(255),
                book_category VARCHAR(255),
                book_price FLOAT,
                book_url VARCHAR(255),
                book_description TEXT,
                book_rating INT,
                product_type VARCHAR(255),
                price_excluded_tax FLOAT,
                price_included_tax FLOAT,
                tax FLOAT,
                availability VARCHAR(255),
                number_of_reviews INT
            );
            """
        )
        self.con.commit()

    def process_item(self, item, spider):
        """
        Stores the book detail item in a DB
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO book_details (
                    book_title,
                    book_category,
                    book_price,
                    book_url,
                    book_description,
                    book_rating,
                    product_type,
                    price_excluded_tax,
                    price_included_tax,
                    tax,
                    availability,
                    number_of_reviews
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    item.get("book_title"),
                    item.get("book_category"),
                    item.get("book_price"),
                    item.get("book_url"),
                    item.get("book_description"),
                    item.get("book_rating"),
                    item.get("product_type"),
                    item.get("price_excluded_tax"),
                    item.get("price_included_tax"),
                    item.get("tax"),
                    item.get("availability"),
                    item.get("number_of_reviews"),
                ),
            )
            self.con.commit()
        except psycopg2.Error as e:
            print("Error:", e)
            self.con.rollback()
        return item

    def close_spider(self, spider):
        """
        Closes the CSV file
        """
        self.cursor.close()
        self.con.close()
