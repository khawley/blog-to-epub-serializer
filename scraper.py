import logging
import os
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from ebooklib import epub

from book_utils import Chapter, Book

logger = logging.getLogger("__main__")

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class Scraper:
    IMAGES_DIR = "images"
    SOUP_DIR = "soups"

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
        preface_chapters = self.add_preface_chapters()
        if preface_chapters:
            chapters = preface_chapters
        for key, url in self.blog_map.items():
            logger.info(f"Processing {key} at url {url}")
            soup = None
            if use_cache:
                try:
                    soup = self.read_soup_from_file(key)
                    logger.info(f"Loaded cached file for {key}")
                except FileNotFoundError:
                    # if local file not found, then look for
                    logger.warning(
                        f"Could not find a file for {key}, fetching from web"
                    )
                    pass
            if not use_cache or not soup:
                soup = self.fetch_page(url, key)
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

    @classmethod
    def read_soup_from_file(
        cls,
        key: float,
    ) -> BeautifulSoup:
        with open(f"{cls.SOUP_DIR}/soup_{key}.html", "r") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        return soup

    @classmethod
    def fetch_page(cls, url: str, key: float) -> BeautifulSoup:
        # confirm the directory exists, creating any intermediates required
        if not os.path.exists(cls.SOUP_DIR):
            os.makedirs(cls.SOUP_DIR)
            logger.info(f"Created directory path {cls.SOUP_DIR}")

        response = requests.get(url)
        with open(f"{cls.SOUP_DIR}/soup_{key}.html", "w") as f:
            f.write(response.text)

        return BeautifulSoup(response.text, "html.parser")

    def parse_chapter_text(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        raise NotImplementedError()

    def add_preface_chapters(self) -> Optional[List[Chapter]]:
        """
        An optional method to add image based chapters to the book.
        Should be implemented in subclasses and return a Chapter
        """

    @classmethod
    def fetch_and_save_img(cls, src: str, key: Optional[float] = None) -> str:
        # determine the full directory path, if supplied a key
        directory = cls.IMAGES_DIR
        if key:
            directory = f"{directory}/{key}"

        # confirm the directory exists, creating any intermediates required
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory path {directory}")

        filename = src.split("/")[-1]
        full_file_path = f"{directory}/{filename}"
        # if a file does not already exist at the name designated
        # - download and store it
        if not os.path.isfile(full_file_path):
            logger.info(
                f"Could not find file {full_file_path}. Fetching from web."
            )
            file = requests.get(src)
            with open(full_file_path, "wb") as f:
                f.write(file.content)
        return full_file_path
