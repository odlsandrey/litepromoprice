#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "odlsandrey"
__email__ = "odlsandrey@gmail.com"

import csv
import time
from time import sleep

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from prom.items import PromItem
from prom.settings import BASE_DATA_XLSX, BASE_DATA_CSV

from prom.moduls.magent import UserAgent
from prom.moduls.price import PromPrice
from prom.moduls.constant import Selector

import pyexcel
import configparser

config = configparser.ConfigParser()
config.read("usersettings.ini")
logfile = 'data/readerror.txt'

def exl2csv():
    start_time = time.time()
    pyexcel.save_as(file_name=BASE_DATA_XLSX,
                    dest_file_name=BASE_DATA_CSV)
    print("INFO : time converter file %s seconds ---" % (
        time.time() - start_time))
    return True


class ManedgerProm(scrapy.Spider):

    name = 'promoprice'
    if exl2csv():
        print("INFO : CSV File is create!")
    sleep(1)

    def __init__(self):

        self.pricelist = config.get("engine", "pricelist")
        self.midllprice = config.get("engine", "midllprice")
        self.stattovar = config.get("engine", "stattovar")
        self.datacsv = BASE_DATA_CSV

        self.sel = Selector()
        self.pp = PromPrice()
        self.ua = UserAgent()

        self.err = True


    custom_settings = {
        'CONCURRENT_REQUESTS' : 4,
        'DOWNLOAD_DELAY' : 21
        }
    apf = "'"
    are = "Articul Error"


    def start_requests(self):
        search = 'https://prom.ua/search?search_term={get}'

        with open(self.datacsv, newline='') as csvfile:
            i = 0
            reader = csv.reader(csvfile, delimiter=',')
            for datastring in reader:
                if i > 0:
                    item = PromItem()
                    item['articul'] = self.pp.clear_text(datastring[0])
                    item['posicion'] = self.pp.clear_text(datastring[1])
                    if self.pricelist == "True":
                        item['price_base'] = self.pp.clear_text(datastring[8])
                    elif self.pricelist == "False":
                        item['price_base'] = self.pp.clear_text(datastring[2])
                    sleep(5.5)
                    query = ('%s+%s' % (item['posicion'],
                                          item['articul']))

                    yield Request(url=search.format(get=query),
                                  headers=self.ua.myheaders(),
                              meta = {"item" : item},
                              callback=self.zerolevel
                                  )
                else: i += 1


    def zerolevel(self, response):
        item = response.meta['item']
        sleep(4)
        price_s, nal_s, head_s = [], [], []
        for n in range(1, 12):
            try:
                data_price = response.xpath(
                    self.sel.price_res.format(n)
                                            ).getall()
                if len(data_price) == 0:
                    try:
                        data_price = response.xpath(
                            self.sel.price_res1.format(n)
                                                    ).getall()
                    except Exception:
                        pass
                if len(data_price) == 0:
                    try:
                        data_price = response.xpath(
                            self.sel.price_res3.format(n)
                                                    ).getall()
                    except Exception:
                        pass
                if len(data_price) == 0:
                    try:
                        data_price = response.xpath(
                            self.sel.price_res4.format(n)
                                                    ).getall()
                    except Exception:
                        pass
                if len(data_price) == 0:
                    try:
                        data_price = response.xpath(
                            self.sel.price_res2.format(n+1)
                                                    ).getall()
                    except Exception:
                        pass

                price_s.append(data_price)
                data_nal = response.xpath(self.sel.nal_res.format(n)).get()
                if data_nal == None:
                    data_nal = response.xpath(
                        self.sel.nal_res2.format(n)
                                              ).get()
                if data_nal == None:
                    data_nal = response.xpath(
                        self.sel.nal_res1.format(n+1)
                                              ).get()
                nal_s.append(data_nal)
                data_head = response.xpath(
                    self.sel.head_res.format(n)
                                          ).get()
                if data_head == None:
                    data_head = response.xpath(
                        self.sel.head_res3.format(n)
                                              ).get()
                if data_head == None:
                    data_head = response.xpath(
                        self.sel.head_res2.format(n)
                                              ).get()
                if data_head == None:
                    data_head = response.xpath(
                        self.sel.head_res2.format(n+1)
                                              ).get()
                head_s.append(data_head)
            except IndexError:
                pass
        dataset = list(zip(nal_s,
                           head_s,
                           self.pp.format_price_string(price_s))
                           )
        dataset_statusbar = self.pp.statusbar(dataset, self.stattovar)
        clear_head = self.pp.valid_head(
            dataset_statusbar,
            item['articul']
                                        )

        if len(clear_head) == 0:
            if self.err == True:
                self.pp.savelogarticle(logfile, response.url, dataset)
            item['price_midl'] = ('%s' % (self.are))
            item['title'] = response.url
            yield item
        else:
            a,b,c = self.pp.getprice(
                            price_arr=clear_head,
                            price_str=item['price_base'],
                            repeat=self.midllprice)

            item['price_min'] = ('%s%s' % (self.apf, a))
            item['price_max'] = ('%s%s' % (self.apf, b))
            item['price_midl'] = ('%s%s' % (self.apf, c))

            if isinstance(c, float):
                _dev = self.pp.str2float(item['price_base'])
                dev = (int(_dev * 100) / 100)
                item['deviation'] = ('%s%s' % (
                    self.apf, (int((dev - c) * 100) / 100))
                                               )
            else:
                item['deviation'] = ('%s%s' % (self.apf, c))
                item['title'] = response.url

            yield item


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(ManedgerProm)
    process.start()
