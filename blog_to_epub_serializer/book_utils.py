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
    no_title_header: bool = False
    add_to_table_of_contents: bool = True

    # should not be set by the user directly
    _echapter: Optional[epub.EpubHtml] = None
    _eimgs: Optional[List[epub.EpubItem]] = None

    def __post_init__(self):
        """
        Runs after the initializer.  Will create the chapter itself to be
        used in the Book
        """
        self._create_echapter()
        self._eimgs = []
        if self.image_paths:
            for image_path in self.image_paths:
                self._create_eimg(image_path)

    @property
    def echapter(self) -> Optional[epub.EpubHtml]:
        return self._echapter

    @property
    def eimgs(self) -> Optional[epub.EpubItem]:
        return self._eimgs

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
        if self.no_title_header:
            ch.content = f"<div>{self.html_content}</div>"
        else:
            ch.content = f"<h1>{self.title}</h1>{self.html_content}"
        self._echapter = ch

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
        self._eimgs.append(
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

    # should not be set by the user directly
    _ebook: Optional[epub.EpubBook] = None

    def __post_init__(self) -> None:
        """
        Runs after the initializer.  Will create the bones of the book
        and add all the chapters.
        """
        self._create_ebook()
        if self.chapters:
            for chapter in self.chapters:
                self._add_chapter_to_ebook(chapter)

    @property
    def ebook(self) -> Optional[epub.EpubBook]:
        return self._ebook

    def _create_ebook(self) -> None:
        """
        Sets up the basic metadata of the book. Including the title, author
        and cover. It also creates an empty (to be filled) table of contents.
        """
        self._ebook = epub.EpubBook()
        self._ebook.set_title(self.title)
        self._ebook.set_language(self.language)
        self._ebook.add_author(self.author)
        self._ebook.spine = []
        if self.cover_img_path:
            self._add_cover()
        self._ebook.spine.append("nav")
        self._ebook.toc = []

    def _add_cover(self):
        # sets the cover when closed/on hover
        self._ebook.set_cover(
            "image.jpg",
            open(self.cover_img_path, "rb").read(),
            # setting to False here to manually add the page
            create_page=False,
        )

        # create the cover html manually, so we can change the linear value
        cover_html = epub.EpubCoverHtml(
            image_name=self.cover_img_path,
        )
        # this is a bug (in my opinion) in the source library
        # when set to the default False, the cover ends up as the
        # last page of the book
        cover_html.is_linear = True

        # and then manually add the image for the html page
        raw_img = Image.open(self.cover_img_path)
        b = io.BytesIO()
        raw_img.save(b, "jpeg")
        bin_img = b.getvalue()
        img_item = epub.EpubItem(
            uid="cover_image",
            file_name=self.cover_img_path,
            media_type="image/jpeg",
            content=bin_img,
        )

        # finally add them to the book and the cover page to the spine
        self._ebook.add_item(cover_html)
        self._ebook.add_item(img_item)
        self._ebook.spine.append("cover")

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
        if chapter.add_to_table_of_contents:
            self.ebook.toc.append(chapter.echapter)

        for ch_eimg in chapter.eimgs:
            self.ebook.add_item(ch_eimg)
