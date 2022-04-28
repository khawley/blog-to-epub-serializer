import io
import os
from dataclasses import dataclass
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from ebooklib import epub
from PIL import Image

IMAGES_DIR = "images"
SOUP_DIR = "soups"


@dataclass
class Chapter:
    idx: float
    title: str
    html_content: BeautifulSoup
    image_path: Optional[str] = None
    echapter: Optional[epub.EpubHtml] = None
    eimg: Optional[epub.EpubItem] = None

    def __post_init__(self):
        self._create_echapter()
        if self.image_path:
            self._create_eimg()

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

    def _create_eimg(self) -> None:
        raw_img = Image.open(self.image_path)
        b = io.BytesIO()
        raw_img.save(b, "jpeg")
        bin_img = b.getvalue()

        uid = (
            self.image_path.split("/")[0].split(".")[0]
            if "/" in self.image_path
            else self.image_path.split(".")[0]
        )
        self.eimg = epub.EpubItem(
            uid=uid,
            file_name=self.image_path,
            media_type="image/jpeg",
            content=bin_img,
        )


@dataclass
class Book:
    title: str
    author: str
    cover_img_path: Optional[str] = ""
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

        if chapter.eimg:
            self.ebook.add_item(chapter.eimg)


def main(
    title, author, blog_map, epub_name, cover_img_path=None, use_cache=True
):
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
        cover_img_path=cover_img_path,
        chapters=chapters,
    )
    book.finish_book()

    # save book to file
    epub.write_epub(epub_name, book.ebook, {})

    pass


def read_soup_from_file(
    key: float,
) -> BeautifulSoup:
    with open(f"{SOUP_DIR}/soup_{key}.html", "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup


def fetch_page(url: str, key: float) -> BeautifulSoup:
    response = requests.get(url)
    with open(f"{SOUP_DIR}/soup_{key}.html", "w") as f:
        f.write(response.text)

    return BeautifulSoup(response.text, "html.parser")


def parse_chapter_text(soup: BeautifulSoup, chapter_idx: float) -> Chapter:
    article = soup.article
    chapter_title = article.h1.text
    chapter_content = article.find(class_="entry-content")

    img_block = chapter_content.find(class_="wp-block-image")
    local_src = ""
    if img_block:
        if img_block.find("noscript"):
            img_block.find("noscript").replace_with("")
        img = img_block.find("img")
        local_src = fetch_and_save_img(img.attrs["data-src"])
        img.attrs["src"] = local_src

    # ignore the Typo box
    ignore_typo_div = "wp-block-genesis-blocks-gb-container"
    if chapter_content.find(class_=ignore_typo_div):
        chapter_content.find(class_=ignore_typo_div).replace_with("")
    return Chapter(
        idx=chapter_idx,
        title=chapter_title,
        html_content=chapter_content,
        image_path=local_src,
    )


def fetch_and_save_img(src: str) -> str:
    filename = src.split("/")[-1]
    full_file_path = f"{IMAGES_DIR}/{filename}"
    if not os.path.isfile(full_file_path):
        file = requests.get(src)
        with open(full_file_path, "wb") as f:
            f.write(file.content)
    return full_file_path


# main()
