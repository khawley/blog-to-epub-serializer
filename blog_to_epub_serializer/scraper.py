import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from ebooklib import epub

from blog_to_epub_serializer.book_utils import Chapter, Book

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

REPO_BASE = Path(__file__).resolve().parent.parent
LOCAL_CACHE = f"{REPO_BASE}/local_cache"


class Scraper:
    # directories in relation to repo base
    SCRAPER_CACHE = LOCAL_CACHE

    def __init__(
        self,
        title: str,
        author: str,
        blog_map: Dict[float, str],
        epub_name: str,
        cover_img_path: Optional[str] = None,
    ):
        # used in the epub metadata
        self.title = title
        # used in the epub metadata
        self.author = author

        # dictionary of chapter numbers (float) to html paths
        self.blog_map = blog_map
        # the local file name that will be created
        self.epub_name = epub_name

        # this should be the local path of the image
        self.cover_img_path = cover_img_path

    def run(self, use_cache: bool = True) -> None:
        """
        Start the scraper. Will grab all html + image files, then process and
        save them into an epub.

        :param use_cache: whether to pull everything fresh from the internet
            or use locally downloaded files
        """
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
        epub.write_epub(f"{LOCAL_CACHE}/{self.epub_name}", book.ebook, {})

        pass

    @classmethod
    def read_soup_from_file(
        cls,
        key: float,
    ) -> BeautifulSoup:
        """
        Given the chapter key, fetch the saved html

        :param key: the chapter number page to retrieve
        :return: html/beautifulsoup loaded page
        """
        with open(f"{cls.SCRAPER_CACHE}/soup_{key}.html", "r") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        return soup

    @classmethod
    def fetch_page(cls, url: str, key: float) -> BeautifulSoup:
        """
        Fetch the page from url and save to the SOUP_DIR

        :param url: the blog page that contains the chapter to ingest
        :param key: the chapter number this page represents
        :return: html/beautifulsoup loaded page
        """
        # confirm the directory exists, creating any intermediates required
        if not os.path.exists(cls.SCRAPER_CACHE):
            os.makedirs(cls.SCRAPER_CACHE)
            logger.info(f"Created directory path {cls.SCRAPER_CACHE}")

        response = requests.get(url)
        with open(f"{cls.SCRAPER_CACHE}/soup_{key}.html", "w") as f:
            f.write(response.text)

        return BeautifulSoup(response.text, "html.parser")

    def parse_chapter_text(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        """
        Method to parse the beautiful soup and edit its contents.  Should
        also save any desired images to local storage
        (use self.fetch_and_save_img)

        :param soup: the html soup to parse and edit
        :param chapter_idx: the chapter number this soup represents
        :return: the Chapter ready to be added to the Book
        """
        raise NotImplementedError()

    def add_preface_chapters(self) -> Optional[List[Chapter]]:
        """
        An optional method to add chapters to the beginning of the book.
        The implementor is responsible for creating or parsing html.
        Should be implemented in subclasses and return a Chapter
        """

    @classmethod
    def fetch_and_save_img(cls, src: str, key: Optional[float] = None) -> str:
        """
        Given an image url, download and save the file to local storage.

        :param src: url source of the image to be downloaded and saved
        :param key: the chapter this image relates to. (this is used to prevent
            multiple images sharing the same name across different chapters)
        :return: the local path the image was downloaded to
        """
        # determine the full directory path, if supplied a key
        directory = cls.SCRAPER_CACHE
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
