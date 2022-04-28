from typing import Dict

from bs4 import BeautifulSoup

from book_utils import Chapter
from scraper import Scraper


class TwelveKingdomsScraper(Scraper):
    IMAGES_DIR = "images/twelvekingdoms"
    SOUP_DIR = "soups/twelvekingdoms"

    def parse_chapter_text(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        post = soup.find(class_="post")
        post_title = post.h3.text.strip()
        chapter_title = post_title.replace(f"{self.title},", "").strip()
        chapter_content = post.find(class_="entry-content")
        header_img_title = "風の海 迷宮の岸"

        # Delete the first 3 p tags as they are filler
        p_tags = chapter_content.findAll("p")

        # First p tag is the header image
        header_img = p_tags[0].find("img")
        if header_img and header_img.attrs["title"] == header_img_title:
            # same for every chapter - delete it
            p_tags[0].replace_with("")

        # Second p tag is a reminder of what book this translation is from
        book_info_p = p_tags[1]
        if (
            post_title in book_info_p.text
            and chapter_idx not in dont_skip_headers_chapters
        ):
            # ~same for every chapter remove it after first chapter
            book_info_p.replace_with("")

        # Third p tag is a dash/filler
        dash_p_tag = p_tags[2]
        if (
            dash_p_tag.text == "-"
            and chapter_idx not in dont_skip_headers_chapters
        ):
            dash_p_tag.replace_with("")

        imgs = chapter_content.findAll("img")
        local_srcs = []
        for img in imgs:
            local_src = self.fetch_and_save_img(img.attrs["src"], chapter_idx)
            img.attrs["src"] = local_src
            local_srcs.append(local_src)

        # remove the prev/next pagers
        p_centers = chapter_content.findAll("p", align="center")
        if "Next >>" in p_centers[-1].text:
            p_centers[-1].replace_with("")

        return Chapter(
            idx=chapter_idx,
            title=chapter_title,
            html_content=chapter_content,
            image_paths=local_srcs,
        )


dont_skip_headers_chapters = [0.5, 6.5, 14.0, 15.0, 16.0]

blog_map: Dict[float, str] = {
    0.5: "https://tu-shu-guan.blogspot.com/2004/07/sea-of-wind-shore-of-maze-prologue.html",
    1.0: "https://tu-shu-guan.blogspot.com/2004/08/sea-of-wind-shore-of-maze-chapter-1.html",
    2.0: "https://tu-shu-guan.blogspot.com/2004/08/sea-of-wind-shore-of-maze-chapter-2.html",
    3.0: "https://tu-shu-guan.blogspot.com/2004/08/sea-of-wind-shore-of-maze-chapter-3.html",
    4.0: "https://tu-shu-guan.blogspot.com/2004/09/sea-of-wind-shore-of-maze-chapter-4.html",
    5.0: "https://tu-shu-guan.blogspot.com/2004/09/sea-of-wind-shore-of-maze-chapter-5.html",
    6.0: "https://tu-shu-guan.blogspot.com/2004/09/sea-of-wind-shore-of-maze-chapter-6.html",
    6.5: "https://tu-shu-guan.blogspot.com/2004/09/sea-of-wind-shore-of-maze-afterword-1.html",
    7.0: "https://tu-shu-guan.blogspot.com/2004/10/sea-of-wind-shore-of-maze-chapter-7.html",
    8.0: "https://tu-shu-guan.blogspot.com/2004/10/sea-of-wind-shore-of-maze-chapter-8.html",
    9.0: "https://tu-shu-guan.blogspot.com/2005/03/sea-of-wind-shore-of-maze-chapter-9.html",
    10.0: "https://tu-shu-guan.blogspot.com/2005/04/sea-of-wind-shore-of-maze-chapter-10.html",
    11.0: "https://tu-shu-guan.blogspot.com/2005/05/sea-of-wind-shore-of-maze-chapter-11.html",
    12.0: "https://tu-shu-guan.blogspot.com/2005/06/sea-of-wind-shore-of-maze-chapter-12.html",
    13.0: "https://tu-shu-guan.blogspot.com/2005/06/sea-of-wind-shore-of-maze-chapter-13.html",
    14.0: "https://tu-shu-guan.blogspot.com/2005/06/sea-of-wind-shore-of-maze-epilogue.html",
    15.0: "https://tu-shu-guan.blogspot.com/2005/06/sea-of-wind-shore-of-maze-afterword-2.html",
    16.0: "https://tu-shu-guan.blogspot.com/2004/07/sea-of-wind-shore-of-maze-glossary.html",
}

title = "Sea of the Wind, Shore of the Maze"
author = "Fuyumi Ono"
cover_img_path = "images/twelvekingdoms/cover1.jpg"
epub_name = f"{title} - {author}.epub"

scraper = TwelveKingdomsScraper(
    title=title,
    author=author,
    cover_img_path=cover_img_path,
    blog_map=blog_map,
    epub_name=epub_name,
)

scraper.run()
