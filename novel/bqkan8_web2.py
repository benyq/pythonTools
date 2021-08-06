import os
import asyncio
import time
from urllib import parse, error
import ssl
import requests
from lxml import etree

import fetch_base
from fetch_base import Chapter
from fetch_base import NovelFetcher
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import re

proxies = {
    'https': 'http://127.0.0.1:7890',
    'http': 'http://127.0.0.1:7890'
}
ssl._create_default_https_context = ssl._create_unverified_context


class BQKan8Fetcher(NovelFetcher):
    base_url = "https://www.kubiji.org/"

    novel_headers = {
        'Host': parse.urlparse(base_url).netloc,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.80 Safari/537.36 '
    }

    def __init__(self, novel_name, novel_url):
        super().__init__(novel_name, novel_url)
        self.novel_save_dir = os.path.join(fetch_base.novel_save_dir, self.novel_name) + os.sep

    def fetch_chapter(self):
        print("爬取：", self.novel_url)
        req = requests.get(self.novel_url, headers=self.novel_headers, proxies=proxies)
        req.encoding = 'utf-8'
        resp = req.text
        selector = etree.HTML(resp)
        chapter_xpath_reg = '//h2[text()="{}全文阅读列表"]/following-sibling::dl/dd/a'.format(self.novel_name)
        results = selector.xpath(chapter_xpath_reg)
        data_list = []
        for result in results:
            data_list.append(Chapter(result.text, result.attrib.get('href')))
        print(len(results))
        req = requests.get(self.novel_url+'_2', headers=self.novel_headers, proxies=proxies)
        req.encoding = 'utf-8'
        resp = req.text
        selector = etree.HTML(resp)
        chapter_xpath_reg = '//h2[text()="{}全文阅读列表"]/following-sibling::dl/dd/a'.format(self.novel_name)
        results = selector.xpath(chapter_xpath_reg)
        print(len(results))

        for result in results:
            data_list.append(Chapter(result.text, result.attrib.get('href')))

        return data_list

    async def async_fetch_content(self, index, novel):
        print("爬取：", novel.chapter_url, end="\n")
        #是否已经存在
        if not os.path.exists(os.path.join(self.novel_save_dir, f"{index}_{novel.chapter_name}.txt")):
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url + novel.chapter_url, headers=self.novel_headers) as resp:
                    result = await resp.text(encoding='utf-8', errors='ignore')
                    selector = etree.HTML(result)
                    content_xpath_reg = '//div[@class="content"]/text()'
                    results = selector.xpath(content_xpath_reg)
                    content = ''
                    for result in results[:-2]:
                        content = content + result.lstrip() + "\n"
                    self.save_novel(index, content, novel.chapter_name)

    def fetch_content(self, novel):
        print("爬取：", novel.chapter_url, end="\n")
        req = requests.get(self.base_url + novel.chapter_url, headers=self.novel_headers, proxies=proxies)
        resp = req.text
        selector = etree.HTML(resp)
        content_xpath_reg = '//div[@id="content"]/text()'
        results = selector.xpath(content_xpath_reg)
        content = ''
        for result in results[:-2]:
            content = content + result.lstrip() + "\n"

        return content

    # 将章节内容写入txt
    def save_novel(self, index, content, chapter_name):
        try:
            # with open(self.novel_save_dir + self.novel_name + '.txt', 'a', encoding='utf-8') as f:
            with open(self.novel_save_dir + f"{index}_{chapter_name}" + '.txt', 'a', encoding='utf-8') as f:
                f.write(chapter_name)
                f.write('\n\n')
                f.write(content)
                f.write('\n\n')
        except (error.HTTPError, OSError) as reason:
            print(str(reason))
        else:
            print("下载完成：" + chapter_name)

    def fetch(self):
        if not os.path.exists(self.novel_save_dir):
            os.mkdir(self.novel_save_dir)

        self.chapter_data = self.fetch_chapter()
        print(len(self.chapter_data))
        # with ThreadPoolExecutor(max_workers=20) as pool:
        #     results = pool.map(self.fetch_content, self.chapter_data)
        #     results = list(zip(results, self.chapter_data))
        #     index = 1
        #     for result, novel in results:
        #         print(index, novel.chapter_name, result)
        #         self.save_novel(index, result, novel.chapter_name)
        #         index += 1

        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(self.async_fetch_content(index, chapter)) for index, chapter in
                 enumerate(self.chapter_data)]
        loop.run_until_complete(asyncio.wait(tasks))


def sort_key(s):
    # 排序关键字匹配
    # 匹配开头数字序号
    if s:
        try:
            c = re.findall('^\d+', s)[0]
        except:
            c = -1

        return int(c)


if __name__ == '__main__':
    fetcher = BQKan8Fetcher("神座崛起", "https://www.kubiji.org/142020")
    print(fetch_base.novel_save_dir)
    if not os.path.exists(os.path.join(fetch_base.novel_save_dir, fetcher.novel_name)):
        os.mkdir(os.path.join(fetch_base.novel_save_dir, fetcher.novel_name))
        start = time.time()
        fetcher.fetch()
        end = time.time()
        print(f"《{fetcher.novel_name}》, 下载耗时: ", end - start)
    else:
        # 合并章节
        chapter_list = os.listdir(fetcher.novel_save_dir)
        chapter_list.sort(key=sort_key)
        for chapter in chapter_list:
            with open(fetcher.novel_save_dir + fetcher.novel_name + '.txt', 'a', encoding='utf-8') as novel:
                with open(fetcher.novel_save_dir + chapter, 'r', encoding='utf-8') as item:
                    novel.write(item.read())
                os.remove(fetcher.novel_save_dir + chapter)
