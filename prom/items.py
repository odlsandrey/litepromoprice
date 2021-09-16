#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scrapy

class PromItem(scrapy.Item):

    articul = scrapy.Field()
    posicion = scrapy.Field()
    price_base = scrapy.Field()
    price_min = scrapy.Field()
    price_max = scrapy.Field()
    price_midl = scrapy.Field()
    deviation = scrapy.Field()
    title = scrapy.Field()

    pass


