import io
from dataclasses import dataclass
from typing import List, Optional, Union

from PIL import Image
from bs4 import BeautifulSoup
from bs4.element import Tag
from ebooklib import epub


@dataclass
class Chapter:
    idx: float
    title: str
    html_content: Union[BeautifulSoup, Tag, str]
    image_paths: Optional[List[str]] = None
    echapter: Optional[epub.EpubHtml] = None
    eimgs: Optional[List[epub.EpubItem]] = None

    def __post_init__(self):
        self._create_echapter()
        self.eimgs = []
        if self.image_paths:
            for image_path in self.image_paths:
                self._create_eimg(image_path)

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

    def _create_eimg(self, image_path: str) -> None:
        raw_img = Image.open(image_path)
        b = io.BytesIO()
        raw_img.save(b, "jpeg")
        bin_img = b.getvalue()

        uid = (
            image_path.split("/")[0].split(".")[0]
            if "/" in image_path
            else image_path.split(".")[0]
        )
        self.eimgs.append(
            epub.EpubItem(
                uid=uid,
                file_name=image_path,
                media_type="image/jpeg",
                content=bin_img,
            )
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

        for ch_eimg in chapter.eimgs:
            self.ebook.add_item(ch_eimg)
