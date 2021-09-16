from scrapy import signals
from scrapy.exporters import CsvItemExporter

from prom.settings import DATA_RESULT_CSV, SAVE_RESULT_XLSX, DATA_PRICE_CSV

import datetime
import pyexcel


class PromPipeline(CsvItemExporter):

    def __init__(self):
       self.files = {}
       self.datacsv_ = DATA_PRICE_CSV
       self.datacsv = DATA_RESULT_CSV
       self.outexcel = SAVE_RESULT_XLSX

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open(self.datacsv_, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = [
            'articul',
            'posicion',
            'price_base',
            'price_midl',
            'deviation',
            'price_min',
            'price_max',
            'title'
            ]
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
        print("Spider is closed!")
        return self.csv2exl()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def csv2exl(self):
        print("[{0}] [moduls.csv2exl] INFO: Start of file formation".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        pyexcel.save_as(file_name=self.datacsv,
                    dest_sheet_name="Result price",
                    dest_file_name=self.outexcel)
        return None
