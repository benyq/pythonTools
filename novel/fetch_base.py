import os

# 小说的保存文件夹
novel_save_dir = os.path.join(os.getcwd(), 'novel_cache/')


class Chapter:
    def __init__(self, chapter_name, chapter_url):
        self.chapter_name = chapter_name
        self.chapter_url = chapter_url

    def __str__(self):
        return "章节名:{}, url:{}".format(self.chapter_name, self.chapter_url)


class NovelFetcher:
    chapter_data = []
    content_data = []
    novel_name = ''
    novel_url = ''

    def __init__(self, novel_name, novel_url):
        self.novel_name = novel_name
        self.novel_url = novel_url
