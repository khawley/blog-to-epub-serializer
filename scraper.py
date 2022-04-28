import os
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup
from ebooklib import epub

from book_utils import Chapter, Book

IMAGES_DIR = "images"
SOUP_DIR = "soups"


class Scraper:
    def __init__(
        self,
        title: str,
        author: str,
        blog_map: Dict[float, str],
        epub_name: str,
        cover_img_path: Optional[str] = None,
    ):
        self.title = title
        self.author = author
        self.blog_map = blog_map
        self.epub_name = epub_name
        self.cover_img_path = cover_img_path

    def run(self, use_cache: bool = True):

        chapters = []
        for key, url in self.blog_map.items():
            if not use_cache:
                soup = self.fetch_page(url, key)
            else:
                soup = self.read_soup_from_file(key)
            chapter = self.parse_chapter_text(soup, key)
            chapters.append(chapter)

        book = Book(
            self.title,
            self.author,
            cover_img_path=self.cover_img_path,
            chapters=chapters,
        )
        book.finish_book()

        # save book to file
        epub.write_epub(self.epub_name, book.ebook, {})

        pass

    @staticmethod
    def read_soup_from_file(
        key: float,
    ) -> BeautifulSoup:
        with open(f"{SOUP_DIR}/soup_{key}.html", "r") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        return soup

    @staticmethod
    def fetch_page(url: str, key: float) -> BeautifulSoup:
        response = requests.get(url)
        with open(f"{SOUP_DIR}/soup_{key}.html", "w") as f:
            f.write(response.text)

        return BeautifulSoup(response.text, "html.parser")

    def parse_chapter_text(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        raise NotImplementedError()

    @staticmethod
    def fetch_and_save_img(src: str) -> str:
        filename = src.split("/")[-1]
        full_file_path = f"{IMAGES_DIR}/{filename}"
        if not os.path.isfile(full_file_path):
            file = requests.get(src)
            with open(full_file_path, "wb") as f:
                f.write(file.content)
        return full_file_path
