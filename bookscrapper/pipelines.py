# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


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
                    else adapter.get(field)[0].strip()
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
