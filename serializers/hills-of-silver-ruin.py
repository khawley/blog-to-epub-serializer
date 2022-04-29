"""
This scraper pulls Sea of the Wind, Shore of the Maze - the second
Twelve Kingdoms novel translated by https://tu-shu-guan.blogspot.com/
"""
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from blog_to_epub_serializer.book_utils import Chapter
from blog_to_epub_serializer.scraper import Scraper, LOCAL_CACHE


class HillsOfSilverRuinScraper(Scraper):
    SCRAPER_CACHE = f"{LOCAL_CACHE}/hills-of-silver-ruin"

    # override parent functions
    def parse_chapter_text(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        # glossary is on a different website, and should be parsed differently
        if chapter_idx == 34.0:
            return self.parse_glossary(soup, chapter_idx)

        post = soup.find(id="main")
        chapter_title = post.find("h4").text
        chapter_content = post.find(id="content")

        # remove all 'p' that contain the source page number
        page_numbers = chapter_content.findAll("p", class_="page")
        for page_number in page_numbers:
            page_number.replace_with("")

        # save all images
        imgs = chapter_content.findAll("img")
        local_srcs = []
        for img in imgs:
            web_src = img.attrs["src"]
            # this is a relative url and needs to be absolutified first
            if web_src.startswith("../"):
                web_src = urljoin(
                    # this is not the url for this page, but they all stem from
                    # the same url path
                    "https://www.eugenewoodbury.com/moon/book1/moon1_01.htm",
                    web_src,
                )
            local_src = self.fetch_and_save_img(web_src, chapter_idx)
            img.attrs["src"] = local_src
            local_srcs.append(local_src)

        return Chapter(
            idx=chapter_idx,
            title=chapter_title,
            html_content=chapter_content,
            image_paths=local_srcs,
        )

    def parse_glossary(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        post = soup.find(id="main")
        chapter_title = post.find("h2").text.strip()
        chapter_content = post.find(class_="blogPost")

        # remove the list of blog labels
        chapter_content.find(class_="blogger-labels").replace_with("")

        return Chapter(
            idx=chapter_idx,
            title=chapter_title,
            html_content=chapter_content,
        )

    def add_preface_chapters(self) -> Optional[List[Chapter]]:
        copyright_ = self.add_copyright()
        maps = self.add_maps()
        return [copyright_] + maps

    # new methods just for this class
    def add_copyright(self) -> Chapter:
        style = """
        <style>
                html, body, div, p {
                    font-size: 100%;
                }
                h1 {
                    font-size: x-large;
                    font-weight: bold;
                    font-style: italic;
                    text-align: center;
                    line-height: 1.4em;
                    margin-bottom: 1.5em;
                    margin-top: 0;
                    padding: 0;
                }
                div.bktitle {
                    text-align: center;
                    margin-bottom: 6pt;
                }
                div.bkauthor {
                    text-align: center;
                    font-weight: bold;
                    font-size: large;
                    margin-bottom: 2em;
                }
                div.copy {
                    text-align: justify;
                    font-size: small;
                    line-height: 1.4em;
                    margin-left: 2em;
                    margin-right: 2em;
                    margin-bottom: 1em;
                }
                a:link {
                    COLOR: #0000AA;
                    text-decoration: none;
                }
                a:visited {
                    COLOR: #0000A0;
                    text-decoration: none;
                }
                a:hover {
                    COLOR: #A00000;
                    background-color: transparent;
                    text-decoration: none;
                    border-bottom: 1px solid;
                }
                a.home:link {
                    COLOR: #0000AA;
                    text-decoration: none;
                    border-bottom: 1px solid;
                }
                a.home:visited {
                    COLOR: #0000A0;
                    text-decoration: none;
                    border-bottom: 1px solid;
                }
                a.home:hover {
                    COLOR: #A00000;
                    background-color: transparent;
                    text-decoration: none;
                    border-bottom: 1px solid;
                }
            </style>
        """
        chapter_content = f"""
        {style}
        <div>
            <h1>Hills of Silver Ruin, <br />
                a Pitch Black Moon</h1>
            <div class="bktitle">
                A Twelve Kingdoms novel
            </div>
            <div class="bktitle">
                by
            </div>
            <div class="bkauthor">
                {self.author}
            </div>
            <div class="copy">
                Copyright &copy; 2019 as 白銀の墟 玄の月  (<i>Hakugin no Oka, 
                Kuro no Tsuki </i>) by {self.author}. Translated by Eugene 
                Woodbury. The numbers at the beginning of each chapter reflect 
                the original part/chapter numbering in the Shinchosa editions
                (ISBN: 978-4101240626 / 978-4101240633 / 978-4101240640 / 
                978-4101240657).<br />
            <br />
            Visit <a class="home" href="https://www.eugenewoodbury.com/moon/index.html">
            www.eugenewoodbury.com/moon/index.html</a> for the source version and more
            information about the Twelve Kingdoms series.
          </div>
        </div>
        """
        return Chapter(
            idx=0.2,
            title="Copyright",
            html_content=chapter_content,
            no_title_header=True,
        )

    def add_maps(self) -> List[Chapter]:
        return [
            self.add_map(
                "Twelve Kingdoms",
                "https://www.eugenewoodbury.com/moon/image/12kingdoms_2.gif",
                idx=0.3,
                is_first=True,
            ),
            self.add_map(
                "The Twelve Kingdoms - Illustrated by Xiao Quan",
                "https://www.eugenewoodbury.com/moon/image/12kingdoms.png",
                idx=0.4,
            ),
            self.add_map(
                "Provinces of Tai",
                "https://www.eugenewoodbury.com/moon/image/taikoku.png",
                idx=0.5,
            ),
        ]

    def add_map(
        self, map_name: str, image_url: str, idx: float, is_first: bool = False
    ) -> Chapter:
        local_image = self.fetch_and_save_img(image_url)
        chapter_content = f"""
        <div>
            <h2>{map_name}</h2>
            <img src="{local_image}" alt="{map_name}/>
        </div>
        """
        return Chapter(
            idx=idx,
            title=f"Maps" if is_first else map_name,
            html_content=chapter_content,
            image_paths=[local_image],
            no_title_header=True,
            add_to_table_of_contents=is_first,
        )


blog_map: Dict[float, str] = {}
for i in range(1, 34):
    blog_map[
        float(f"{i:02}")
    ] = f"https://www.eugenewoodbury.com/moon/book1/moon1_{i:02}.htm"

blog_map[
    34.0
] = "https://eugenewoodbury.blogspot.com/2020/04/twelve-kingdoms-glossary.html"

title = "Hills of Silver Ruin, a Pitch Black Moon"
author = "Fuyumi Ono"
epub_name = f"{title} - {author}.epub"
cover_img_path = HillsOfSilverRuinScraper.fetch_and_save_img(
    "https://www.eugenewoodbury.com/moon/image/moon1.jpg"
)

scraper = HillsOfSilverRuinScraper(
    title=title,
    author=author,
    cover_img_path=cover_img_path,
    blog_map=blog_map,
    epub_name=epub_name,
)

scraper.run()
