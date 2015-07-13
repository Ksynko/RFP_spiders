# -*- coding: utf-8 -*-
from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst



class RpfSpidersItem(Item):
    title = Field(output_processor=TakeFirst())
    URL = Field(output_processor=TakeFirst())
    posted = Field(output_processor=TakeFirst())
    response_due = Field(output_processor=TakeFirst())
    classification_code = Field(output_processor=TakeFirst())
    NAICS_code = Field(output_processor=TakeFirst())
    set_aside_code = Field(output_processor=TakeFirst())
    contracting_office_address = Field(output_processor=TakeFirst())
    description = Field(output_processor=TakeFirst())
    point_of_contact = Field()
