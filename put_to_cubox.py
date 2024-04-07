from time import sleep
import mysql.connector
import requests
import logging
import mysql.connector
import json
from public_method import connect_to_database
from datetime import datetime, timezone, timedelta


def query_unpushed_article():
    # 查询数据库中未推送且按优先级排序的文章
    connection = connect_to_database()
    if connection is not None:
        cursor = connection.cursor(dictionary=True)
        # 添加ORDER BY子句对结果按priority字段降序排序
        cursor.execute("SELECT * FROM rss_articles WHERE pushed = FALSE ORDER BY priority DESC")
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        logging.info(f"【查询成功】 Found {len(result)} unpushed articles sorted by priority.")
        return result


class PutToCubox:
    def __init__(self, cubox_url):
        self.cubox_url = cubox_url
        self.query_list = query_unpushed_article()
        self.push_list = []

    def process_selected_data(self):
        try:
            for article in self.query_list:
                tags_str = article.get('tags', '无标题')
                description = article.get('published_at', datetime(1970, 1, 1)).strftime('%Y-%m-%d %H:%M:%S') + "\n" + article.get('description', '无描述')
                if tags_str:
                    tags_list = tags_str.split(',')
                else:
                    tags_list = ['default']
                content_dict = {
                    'type': 'url',
                    'content': article.get('link', '未知链接'),
                    'title': article.get('title', '无标题'),
                    'description': description,
                    'tags': tags_list,
                    'folder': article.get('folder', '默认')
                }
                self.push_list.append(content_dict)
        except Exception as e:
            logging.info(f"【查询失败】 数据库查询到的文章失败：{e}")
            return

    def send_post_request(self, json_data, retries=3, timeout=5):
        for attempt in range(retries):
            try:
                sleep(1)
                response = requests.post(self.cubox_url, json=json_data, timeout=timeout)
                if json.loads(response.text)['code'] == 200:
                    logging.info(f"【状态】 已发送至Cubox, {response.text}")
                    return True

                elif json.loads(response.text)['code'] == -3030:
                    logging.info(f"【状态】 已超过上传限制。")
                    return False
                else:
                    logging.info(f"【状态】 上传失败，状态码: {json.loads(response.text)['code']}。")
            except requests.exceptions.RequestException as e:
                logging.info(f"{json_data['title']}：请求异常 {e}。")
        logging.info("【状态】 已达到最大尝试次数，请求未成功。")
        return False

    def push_unpushed_articles(self):
        self.process_selected_data()
        self.push_log_to_cubox()
        connection = connect_to_database()
        if connection is not None:
            cursor = connection.cursor(dictionary=True)
            for article in self.push_list:
                # 在这里实现推送逻辑
                try:
                    if self.send_post_request(article):
                        # 假设推送成功：
                        cursor.execute("UPDATE rss_articles SET pushed = TRUE WHERE title = %s", (article['title'],))
                        connection.commit()
                        logging.info(f"Article '{article['title']}' pushed successfully. The database push status has been modified.")
                    else:
                        logging.info(f"Article '{article['title']}' pushed finally failed.")
                except mysql.connector.Error as e:
                    logging.info(f"Failed to push articles. MySQL Error: {e}")
            cursor.close()
            connection.close()

    def push_log_to_cubox(self):
        china_timezone = timezone(timedelta(hours=8))
        date_string = datetime.now(china_timezone).strftime('%Y-%m-%d %H:%M:%S')
        log_content = {
            'type': 'memo',
            'content': f"{date_string} 今日定时任务成功运行！",
            'title': f'{date_string} 今日RSS订阅任务成功运行！',
            'description': f'{date_string} RSS订阅日志，本次共找到{len(self.push_list)}篇文章',
            'tags': ['logs'],
            'folder': 'RSS Log'
        }
        self.send_post_request(log_content)
