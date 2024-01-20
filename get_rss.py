import re
import requests
import logging
from urllib.parse import urljoin
from datetime import datetime
from feedgen.feed import FeedGenerator


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://book.douban.com/latest'
TOTAL_PAGE = 1

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
    #logging.info('scraping %s...', url)
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
        #logging.info('get detail url %s', detail_url)
        yield detail_url

def scrape_detail(url):
    return scrape_page(url)

def parse_detail(html):
    # re.S 用于多行匹配，也就是 html 有换行的时候可以用它
    cover_pattern = re.compile(
        'class="nbg".*?<img.*?src="(.*?)".*?title="点击看大图".*?>', re.S)
    name_pattern = re.compile(
        '<h1>.*?>(.*?)<.*?</h1>', re.S
    )
    info_patten = re.compile('<div id="info".*?>(.*?)</div>', re.S)
    content_patten = re.compile('<div class="intro">(.*?)</div>', re.S)

    cover = re.search(cover_pattern, html).group(1).strip() if re.\
        search(cover_pattern, html) else None
    name = re.search(name_pattern, html).group(1).strip() if re.\
        search(name_pattern, html) else None
    #info = None
    info = re.search(info_patten, html).group(1).strip() if re.search(info_patten, html) else None
    content = re.search(content_patten, html).group(1).strip() if re.search(content_patten, html) else None
    return {
        'cover': cover,
        'name': name,
        'info': info,
        'content': content,
    }


def main():
    # 使用FeedGenerator创建RSS源
    fg = FeedGenerator()
    fg.title('豆瓣新书速递')
    fg.link(href=BASE_URL, rel='alternate')
    fg.description('豆瓣新书速递，测试版')

    for page in range(1, TOTAL_PAGE+1):
        index_html = scrape_index(page)
        detail_urls = parse_index(index_html)
        for detail_url in detail_urls:
            detail_html = scrape_detail(detail_url)
            data = parse_detail(detail_html)
            logging.info('get detail data %s', data)

            # 添加条目
            fe = fg.add_entry()
            fe.id(detail_url)
            fe.title(data['name'])
            fe.link(href=detail_url)
            fe.description(data['info'])
            fe.content(data['content'])
            #fe.pubDate(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            fe.enclosure(url=data['cover'], type='image/jpeg')

    # 生成RSS源的XML文件
    rss_xml_bytes = fg.rss_str(pretty=True)

    # 将XML内容转换为字符串
    rss_xml_str = rss_xml_bytes.decode('utf-8')

    # 将字符串内容写入文件
    with open('rss_feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss_xml_str)

    print('RSS源已生成并保存到rss_feed.xml文件。')

if __name__=='__main__':
    main()


"""
# 检查请求是否成功
if response.status_code == 200:


    # 生成RSS源的XML文件
    rss_xml = fg.rss_str(pretty=True)

    # 将XML内容写入文件
    with open('rss_feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss_xml)
        
        

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