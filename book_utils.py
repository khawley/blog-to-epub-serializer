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
        """
        Runs after the initializer.  Will create the chapter itself to be
        used in the Book
        """
        self._create_echapter()
        self.eimgs = []
        if self.image_paths:
            for image_path in self.image_paths:
                self._create_eimg(image_path)

    @property
    def xhtml(self) -> str:
        """
        The full html file name for this chapter

        :return: formatted string
        """
        return f"{self.ch_idx}.html"

    @property
    def ch_idx(self) -> str:
        """
        Prepend 'ch_' and the zero padded chapter idx.  To be used when naming
        the epub internal files.

        :return: formatted string
        """
        return f"ch_{self.idx:02}"

    def _create_echapter(self) -> None:
        """
        Adds title to the beginning of the html, and then the html content
        """
        ch = epub.EpubHtml(title=self.title, file_name=self.xhtml)
        ch.content = f"<h1>{self.title}</h1>{self.html_content}"
        self.echapter = ch

    def _create_eimg(self, image_path: str) -> None:
        """
        Creates the ebook version of an image by loading it into binary, then
        appends an epub image to the attributes list.

        :param image_path:  the local path to the image
        """
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

    def __post_init__(self) -> None:
        """
        Runs after the initializer.  Will create the bones of the book
        and add all the chapters.
        """
        self._create_ebook()
        if self.chapters:
            for chapter in self.chapters:
                self._add_chapter_to_ebook(chapter)

    def _create_ebook(self) -> None:
        """
        Sets up the basic metadata of the book. Including the title, author
        and cover. It also creates an empty (to be filled) table of contents.
        """
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
        """
        Should be used to add chapters to Book, instead of touching the
        attribute directly. This will properly add the chapter to the ebook.
        It will always be added after all the previous chapters in the list.

        :param chapter: The chapter to be added
        """
        if not self.chapters:
            self.chapters = []
        self.chapters.append(chapter)
        self._add_chapter_to_ebook(chapter)

    def _add_chapter_to_ebook(self, chapter: Chapter) -> None:
        """
        Private method, this adds the chapter directly to the ebook and does
        not manipulate the attribute list.  It also adds any images from the
        chapter to the ebook.

        :param chapter: The chapter to be added
        """
        self.ebook.add_item(chapter.echapter)
        self.ebook.spine.append(chapter.echapter)
        self.ebook.toc.append(chapter.echapter)

        for ch_eimg in chapter.eimgs:
            self.ebook.add_item(ch_eimg)
