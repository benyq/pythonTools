import ssl
import os
import time

import requests
from lxml import etree
import fetch_base
from urllib import parse, error
from fetch_base import Chapter
import aiohttp
import asyncio

proxies = {
    'https': 'http://127.0.0.1:7890',
    'http': 'http://127.0.0.1:7890'
}
ssl._create_default_https_context = ssl._create_unverified_context


class NovelFetcher:
    chapter_data = []
    novel_name = ''
    novel_url = ''
    novel_save_dir = ''

    def __init__(self, base_url, chapter_xpath_reg, content_xpath_reg, site_encoding,
                 chapter_paging=False, chapter_suffix="_"):
        self.base_url = base_url
        self.novel_headers = {
            'Host': parse.urlparse(base_url).netloc,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.80 Safari/537.36 '
        }
        self.chapter_paging = chapter_paging
        self.chapter_suffix = chapter_suffix
        self.site_encoding = site_encoding
        self.chapter_xpath_reg = chapter_xpath_reg
        self.content_xpath_reg = content_xpath_reg

    def fetch(self, novel_name, novel_url, ):
        self.novel_url = novel_url
        self.novel_name = novel_name
        self.novel_save_dir = os.path.join(fetch_base.novel_save_dir, self.novel_name) + os.sep
        self.fetch_content()

    def fetch_chapter(self):
        page = 1
        if not self.chapter_paging:
            self.chapter_data = self.do_fetch_chapter(0)
        else:
            while True:
                chapter_data = self.do_fetch_chapter(page)
                page += 1
                if len(chapter_data) > 0:
                    self.chapter_data += chapter_data
                else:
                    break
        print(len(self.chapter_data))

    async def async_fetch_content(self, index, novel):
        if not os.path.exists(os.path.join(self.novel_save_dir, f"{index}_{novel.chapter_name}.txt")):
            print("爬取：", novel.chapter_url, end="\n")
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url + novel.chapter_url, headers=self.novel_headers) as resp:
                    result = await resp.text(encoding=self.site_encoding, errors='ignore')
                    selector = etree.HTML(result)
                    results = selector.xpath(self.content_xpath_reg)
                    content = ''
                    for result in results[:-2]:
                        content = content + result.lstrip() + "\n"
                    self.save_novel(index, content, novel.chapter_name)

    def fetch_content(self):
        self.fetch_chapter()
        if not os.path.exists(self.novel_save_dir):
            os.mkdir(self.novel_save_dir)
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(self.async_fetch_content(index, chapter)) for index, chapter in
                 enumerate(self.chapter_data)]
        loop.run_until_complete(asyncio.wait(tasks))
        # 下载完成，准备合并
        if len(os.listdir(fetcher.novel_save_dir)) >= len(fetcher.chapter_data):
            fetcher.merge_chapter()
        else:
            fetcher.fetch_content()

    # 将章节内容写入txt
    def save_novel(self, index, content, chapter_name):
        try:
            with open(self.novel_save_dir + f"{index}_{chapter_name}" + '.txt', 'a', encoding='utf-8') as f:
                f.write(chapter_name)
                f.write('\n\n')
                f.write(content)
                f.write('\n\n')
        except (error.HTTPError, OSError) as reason:
            print(str(reason))
        else:
            print("下载完成：" + chapter_name)

    def do_fetch_chapter(self, page):
        if self.chapter_paging:
            fetch_url = self.base_url + self.novel_url + self.chapter_suffix + str(page)
        else:
            fetch_url = self.base_url + self.novel_url
        req = requests.get(fetch_url, headers=self.novel_headers,
                           proxies=proxies)
        req.encoding = self.site_encoding
        resp = req.text
        selector = etree.HTML(resp)
        results = selector.xpath(self.chapter_xpath_reg)
        data_list = []
        for result in results:
            data_list.append(Chapter(result.text, result.attrib.get('href')))
        return data_list

    def merge_chapter(self):
        chapter_list = os.listdir(self.novel_save_dir)
        chapter_list.sort(key=fetch_base.sort_key)
        for chapter in chapter_list:
            with open(self.novel_save_dir + self.novel_name + '.txt', 'a', encoding='utf-8') as novel:
                with open(self.novel_save_dir + chapter, 'r', encoding='utf-8') as item:
                    novel.write(item.read())
                os.remove(self.novel_save_dir + chapter)


def bqkan8():
    return NovelFetcher("https://www.bqkan8.com/", "//dt[contains(text(), '正文卷')]/following-sibling::dd/a",
                        '//div[@id="content"]/text()', 'gbk')


def kubiji():
    return NovelFetcher("https://www.kubiji.org/",
                        '//h2[@class="book_article_texttitle"]/following-sibling::dl/dd/a',
                        '//div[@class="content"]/text()', 'utf-8', True)


if __name__ == '__main__':
    if not os.path.exists(fetch_base.novel_save_dir):
        os.mkdir(fetch_base.novel_save_dir)

    # fetcher = NovelFetcher("https://www.kubiji.org/",
    #                        '//h2[@class="book_article_texttitle"]/following-sibling::dl/dd/a',
    #                        '//div[@class="content"]/text()', 'utf-8', True)
    # start = time.time()
    # fetcher.fetch("神座崛起", "142020")
    # end = time.time()
    # print(f"{fetcher.novel_name}下载耗时: {end - start} s")

    fetcher = NovelFetcher("https://www.bqkan8.com/", "//dt[contains(text(), '正文卷')]/following-sibling::dd/a",
                           '//div[@id="content"]/text()', 'gbk')
    start = time.time()
    fetcher.fetch("荣耀骑士团", "4_4024")
    end = time.time()
    print(f"{fetcher.novel_name}下载耗时: {end - start} s")
