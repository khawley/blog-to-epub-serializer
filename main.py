import io
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from ebooklib import epub
from PIL import Image


blog_map: Dict[float, str] = {
    1.0: "https://www.ilona-andrews.com/2021/happy-holidays-4/",
    2.0: "https://www.ilona-andrews.com/2021/chapter-2/",
    3.0: "https://www.ilona-andrews.com/2022/chapter-3/",
    4.0: "https://www.ilona-andrews.com/2022/chapter-4-part-1/",
    4.5: "https://www.ilona-andrews.com/2022/chapter-4-part-2/",
    5.0: "https://www.ilona-andrews.com/2022/chapter-5/",
    6.0: "https://www.ilona-andrews.com/2022/chapter-6-part-1/",
    6.5: "https://www.ilona-andrews.com/2022/chapter-6-part-2/",
    7.0: "https://www.ilona-andrews.com/2022/chapter-7/",
    8.0: "https://www.ilona-andrews.com/2022/chapter-8-part-1/",
    8.5: "https://www.ilona-andrews.com/2022/chapter-8-part-2/",
    9.0: "https://www.ilona-andrews.com/2022/chapter-9-part-1/",
}


@dataclass
class Chapter:
    idx: float
    title: str
    html_content: BeautifulSoup
    image_path: Optional[str] = None
    echapter: Optional[epub.EpubHtml] = None

    def __post_init__(self):
        self._create_echapter()

    @property
    def xhtml(self) -> str:
        return f"{self.ch_idx }.html"

    @property
    def ch_idx(self) -> str:
        return f"ch_{self.idx:02}"

    def _create_echapter(self) -> None:
        ch = epub.EpubHtml(title=self.title, file_name=self.xhtml)
        ch.content = f"<h1>{self.title}</h1>{self.html_content}"
        self.echapter = ch


@dataclass
class Book:
    title: str
    author: str
    cover_img_path: str = ""
    language: str = "en"
    chapters: Optional[List[Chapter]] = None
    ebook: Optional[epub.EpubBook] = None

    def __post_init__(self):
        self._create_ebook()
        if self.chapters:
            for chapter in self.chapters:
                self._add_chapter_to_ebook(chapter)

    def _create_ebook(self):
        ebook = epub.EpubBook()
        ebook.set_title(self.title)
        ebook.set_language(self.language)
        ebook.add_author(self.author)
        ebook.spine = []
        if self.cover_img_path:
            ebook.set_cover(
                "image.jpg", open(self.cover_img_path, "rb").read()
            )
            ebook.spine.append("cover")
        ebook.spine.append("nav")
        ebook.toc = []
        # title_page = epub.Link("title.xhtml", 'Title', 'title')
        self.ebook = ebook

    def finish_book(self):
        # add default NCX and Nav file
        self.ebook.add_item(epub.EpubNcx())
        self.ebook.add_item(epub.EpubNav())

        # define CSS style
        style = "BODY {color: white;}"
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )

        # add CSS file
        self.ebook.add_item(nav_css)

    def add_chapter(self, chapter: Chapter) -> None:
        if not self.chapters:
            self.chapters = []
        self.chapters.append(chapter)
        self._add_chapter_to_ebook(chapter)

    def _add_chapter_to_ebook(self, chapter: Chapter) -> None:
        self.ebook.add_item(chapter.echapter)
        self.ebook.spine.append(chapter.echapter)
        self.ebook.toc.append(chapter.echapter)


def main(use_cache=True):
    title = "Innkeeper Chronicles - Sweep of the Heart"
    author = "Ilona Andrews"

    chapters = []
    for key, url in blog_map.items():
        if not use_cache:
            soup = fetch_page(url, key)
        else:
            soup = read_soup_from_file(key)
        chapter = parse_chapter_text(soup, key)
        chapters.append(chapter)

    book = Book(
        title,
        author,
        cover_img_path="A-dahl-cover-art-chop.jpg",
        chapters=chapters,
    )
    book.finish_book()

    # save book to file
    epub.write_epub("Sweep of the Heart.epub", book.ebook, {})

    pass


def read_soup_from_file(
    key: float,
) -> BeautifulSoup:
    with open(f"soup_{key}.html", "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup


def fetch_page(url: str, key: float) -> BeautifulSoup:
    response = requests.get(url)
    with open(f"soup_{key}.html", "w") as f:
        f.write(response.text)

    return BeautifulSoup(response.text, "html.parser")


def parse_chapter_text(soup: BeautifulSoup, chapter_idx: float) -> Chapter:
    article = soup.article
    chapter_title = article.h1.text
    chapter_content = article.find(class_="entry-content")

    if chapter_content.find(class_="wp-block-image"):
        chapter_content.find(class_="wp-block-image").replace_with("")

    # ignore the Typo box
    ignore_typo_div = "wp-block-genesis-blocks-gb-container"
    if chapter_content.find(class_=ignore_typo_div):
        chapter_content.find(class_=ignore_typo_div).replace_with("")
    return Chapter(
        idx=chapter_idx,
        title=chapter_title,
        html_content=chapter_content,
        has_image=True,
    )


def fetch_and_save_file(src: str) -> str:
    filename = src.split("/")[-1]
    full_file_path = f"images/{filename}"
    if not os.path.isfile(filename):
        file = requests.get(src)
        with open(full_file_path, "wb") as f:
            f.write(file.content)
    return full_file_path


main()
