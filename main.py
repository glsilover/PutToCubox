import logging
from public_method import china_time_converter
from put_to_cubox import PutToCubox
from datetime import datetime, timezone, timedelta
# import sys


docker_path = '/app/rss/'

# 设置时区

china_timezone = timezone(timedelta(hours=8))
timestamp = datetime.now(china_timezone).strftime('%Y-%m-%d_%H-%M-%S')


# 配置日志
logging.Formatter.converter = china_time_converter

log_filename = f"{docker_path}docker_log_rss_insert_db_{timestamp}.txt"
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    unpushed_article = PutToCubox('')
    unpushed_article.push_unpushed_articles()
    logging.info("全部处理完成\n")
