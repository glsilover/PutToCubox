import mysql.connector
from mysql.connector import Error
from datetime import datetime, timezone, timedelta
import logging

china_timezone = timezone(timedelta(hours=8))


def china_time_converter(*args):
    """
    自定义时间转换器，将UTC时间转换为北京时间。
    """
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(china_timezone).timetuple()


def connect_to_database(internet=False):
    if internet:
        host = ''
        port = 48176
    else:
        host = ''
        port = 3306
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database='rss',
            user='admin',
            password='',
            ssl_disabled=True
        )
        if connection.is_connected():
            return connection
    except Error as e:
        logging.info(f"Error connecting to MySQL: {e}")
        return None