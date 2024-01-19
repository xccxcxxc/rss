import re
import requests
import logging
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://book.douban.com/latest'
TOTAL_PAGE = 2

myheaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,ms;q=0.5',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'book.douban.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
}

def scrape_page(url):
    logging.info('scraping %s...', url)
    try:
        response = requests.get(url, headers=myheaders)
        if response.status_code == 200:
            return response.text
        logging.error('get invalid status code %s while scraping %s',
                      response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url,
                      exc_info=True)

def scrape_index(page):
    index_url = f'{BASE_URL}/?p={page}'
    return scrape_page(index_url)

def parse_index(html):
    pattern = re.compile('<a.*?class="fleft".*?href="(.*?)">')
    items = re.findall(pattern, html)
    if not items:
        return []
    for item in items:
        detail_url = item
        logging.info('get detail url %s', detail_url)
        yield detail_url

def main():
    for page in range(1, TOTAL_PAGE+1):
        index_html = scrape_index(page)
        detail_urls = parse_index(index_html)
        logging.info('detail urls %s', list(detail_urls))

if __name__=='__main__':
    main()


"""
# 检查请求是否成功
if response.status_code == 200:
    # 使用FeedGenerator创建RSS源
    fg = FeedGenerator()
    fg.title('Example Website News')
    fg.link(href=BASE_URL, rel='alternate')
    fg.description('Latest news from Example Website')

    # 将网页内容添加到RSS源中
    entry = fg.add_entry()
    entry.title('Latest News')
    entry.link(href=BASE_URL)
    entry.description(response.text)

    # 生成RSS源的XML文件
    rss_xml_bytes = fg.rss_str(pretty=True)

    # 将XML内容转换为字符串
    rss_xml_str = rss_xml_bytes.decode('utf-8')

    # 将字符串内容写入文件
    with open('rss_feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss_xml_str)

    print('RSS源已生成并保存到rss_feed.xml文件。')

else:
    print(f'请求失败，状态码：{response.status_code}')

"""