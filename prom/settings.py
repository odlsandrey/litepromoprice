
BOT_NAME = 'promoprice'

SPIDER_MODULES = ['prom.spiders']
NEWSPIDER_MODULE = 'prom.spiders'
ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    #'prom.middlewares.PromDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware':None,
}

ITEM_PIPELINES = {
    'prom.pipelines.PromPipeline': 300,
}

SAVE_RESULT_XLSX = 0
DATA_RESULT_CSV = 0

BASE_DATA_XLSX = 0
BASE_DATA_CSV = 0

DATA_PRICE_CSV = 0
