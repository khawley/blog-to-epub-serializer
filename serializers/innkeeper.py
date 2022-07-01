from typing import Dict

from bs4 import BeautifulSoup

from blog_to_epub_serializer.book_utils import Chapter
from blog_to_epub_serializer.scraper import Scraper, LOCAL_CACHE


class InnkeeperScraper(Scraper):
    SCRAPER_CACHE = f"{LOCAL_CACHE}/innkeeper"

    def parse_chapter_text(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        article = soup.article
        chapter_title = article.h1.text
        chapter_content = article.find(class_="entry-content")

        img_blocks = chapter_content.findAll(class_="wp-block-image")
        local_srcs = []
        for img_block in img_blocks:
            if img_block.find("noscript"):
                img_block.find("noscript").replace_with("")
            img = img_block.find("img")
            local_src = self.fetch_and_save_img(
                img.attrs["data-src"], chapter_idx
            )
            img.attrs["src"] = local_src
            local_srcs.append(local_src)

        # ignore the Typo box
        ignore_typo_div = "wp-block-genesis-blocks-gb-container"
        if chapter_content.find(class_=ignore_typo_div):
            chapter_content.find(class_=ignore_typo_div).replace_with("")
        return Chapter(
            idx=chapter_idx,
            title=chapter_title,
            html_content=chapter_content,
            image_paths=local_srcs,
        )


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
    9.5: "https://www.ilona-andrews.com/2022/chapter-9-part-2-2/",
    10.0: "https://www.ilona-andrews.com/2022/chapter-10-part-1-2/",
    10.5: "https://www.ilona-andrews.com/2022/chapter-10-part-2-2/",
    11.0: "https://www.ilona-andrews.com/2022/chapter-11-part-1/",
    11.5: "https://www.ilona-andrews.com/2022/chapter-11-part-2/",
    12.0: "https://www.ilona-andrews.com/2022/chapter-12-2/",
    13.0: "https://www.ilona-andrews.com/2022/chapter-13/",
    14.0: "https://www.ilona-andrews.com/2022/chapter-14-part-1-5/",
    14.5: "https://www.ilona-andrews.com/2022/chapter-14-part-2/",
    15.0: "https://www.ilona-andrews.com/2022/chapter-15/",
    16.0: "https://www.ilona-andrews.com/2022/chapter-16/",
    17.0: "https://www.ilona-andrews.com/2022/chapter-17/",
    18.0: "https://www.ilona-andrews.com/2022/chapter-18-part-1/",
    18.5: "https://www.ilona-andrews.com/2022/chapter-18-part-2/",
}

title = "Innkeeper Chronicles - Sweep of the Heart"
author = "Ilona Andrews"
cover_img_path = f"{LOCAL_CACHE}/innkeeper/A-dahl-cover-art-chop.jpg"
epub_name = "Sweep of the Heart.epub"

scraper = InnkeeperScraper(
    title=title,
    author=author,
    cover_img_path=cover_img_path,
    blog_map=blog_map,
    epub_name=epub_name,
)

scraper.run()
