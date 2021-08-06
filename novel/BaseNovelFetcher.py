import ssl
import os
import requests
from lxml import etree
import fetch_base
from urllib import parse, error
from fetch_base import Chapter

proxies = {
    'https': 'http://127.0.0.1:7890',
    'http': 'http://127.0.0.1:7890'
}
ssl._create_default_https_context = ssl._create_unverified_context


class BaseNovelFetcher:
    chapter_data = []

    def __init__(self, base_url, novel_name, novel_url, site_encoding, chapter_paging=False, chapter_suffix="_"):
        self.novel_name = novel_name
        self.novel_url = novel_url
        self.base_url = base_url
        self.novel_save_dir = os.path.join(fetch_base.novel_save_dir, self.novel_name) + os.sep
        self.novel_headers = {
            'Host': parse.urlparse(base_url).netloc,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.80 Safari/537.36 '
        }
        self.chapter_paging = chapter_paging
        self.chapter_suffix = chapter_suffix
        self.site_encoding = site_encoding

    def fetch_chapter(self):
        page = 1
        if not self.chapter_paging:
            self.chapter_data = self.do_fetch_chapter(0)
        while True:
            chapter_data = self.do_fetch_chapter(page)
            page += 1
            if len(chapter_data) > 0:
                self.chapter_data += chapter_data
            else:
                break
        print(len(self.chapter_data))

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
        chapter_xpath_reg = '//h2[@class="book_article_texttitle"]/following-sibling::dl/dd/a'
        results = selector.xpath(chapter_xpath_reg)
        data_list = []
        for result in results:
            data_list.append(Chapter(result.text, result.attrib.get('href')))
        return data_list


if __name__ == '__main__':
    fetcher = BaseNovelFetcher("https://www.kubiji.org/", "神座崛起", "142020", "utf-8", True)
    fetcher.fetch_chapter()
