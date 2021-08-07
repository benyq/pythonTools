import os
import re

# 小说的保存文件夹
novel_save_dir = os.path.join(os.getcwd(), 'novel_cache/')


class Chapter:
    def __init__(self, chapter_name, chapter_url):
        self.chapter_name = chapter_name
        self.chapter_url = chapter_url

    def __str__(self):
        return "章节名:{}, url:{}".format(self.chapter_name, self.chapter_url)


def sort_key(s):
    # 排序关键字匹配
    # 匹配开头数字序号
    if s:
        try:
            c = re.findall('^\d+', s)[0]
        except:
            c = -1

        return int(c)
