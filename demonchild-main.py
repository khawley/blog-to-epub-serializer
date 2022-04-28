from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from book_utils import Chapter
from scraper import Scraper


class TwelveKingdomsScraper(Scraper):
    IMAGES_DIR = "images/demonchild"
    SOUP_DIR = "soups/demonchild"

    # override parent functions
    def parse_chapter_text(
        self, soup: BeautifulSoup, chapter_idx: float
    ) -> Chapter:
        post = soup.find(class_="post")
        post_title = post.h3.text.strip()
        chapter_title = post_title.replace(f"{self.title},", "").strip()
        chapter_content = post.find(class_="entry-content")
        header_img_title = "魔性の子"

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

    def add_preface_chapters(self) -> Optional[List[Chapter]]:
        copyright_ = self.add_copyright()
        return [copyright_]

    # new methods just for this class
    def add_copyright(self) -> Optional[Chapter]:
        cover_2 = self.fetch_and_save_img(
            "https://lh6.googleusercontent.com/_4ORonPYBrqQ/Tb-vb19znYI/AAAAAAAAAGM/8UIPeIt4WUA/s800/jkcover02b.jpg"
        )
        local_srcs = [cover_2]
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
        <html>
        <head>
            {style}
        </head>
        <body>
        <div>
            <h1>Demon Child</h1>
            <div class="bktitle">
                A Twelve Kingdoms related novel
            </div>
            <div class="bktitle">
                by
            </div>
            <div class="bkauthor">
                Fuyumi Ono
            </div>
            <div class="copy">
                Copyright &copy; 1991 as 魔性の子 (<i>Mashou no Ko</i>)
                by Fuyumi Ono. Translated by Mina. The numbers at
                the beginning of each chapter reflect the original part/chapter
                numbering in the Kodansha Paperbacks edition
                (ISBN: 978-4-06-255114-4/978-4-06-255120-5).<br />
            <br />
            Visit <a class="home" href="https://tu-shu-guan.blogspot.com">
            tu-shu-guan.blogspot.com</a> for the source version and more
            information about the Twelve Kingdoms series.
          </div>
        </div>
        <div>
            <h2>Cover of Volume 2</h2>
            <img src="{cover_2}" alt="Cover2"/>
        </div>
        </body>
        </html>
        """
        return Chapter(
            idx=0.1,
            title="",
            html_content=chapter_content,
            image_paths=local_srcs,
        )


dont_skip_headers_chapters = [0.5, 0.6, 12.0, 13.0]

blog_map: Dict[float, str] = {
    0.5: "https://tu-shu-guan.blogspot.com/2006/08/demon-child-prefacing-poem.html",
    0.6: "https://tu-shu-guan.blogspot.com/2005/06/demon-child-prologue.html",
    1.0: "https://tu-shu-guan.blogspot.com/2005/11/demon-child-chapter-1.html",
    2.0: "https://tu-shu-guan.blogspot.com/2006/01/demon-child-chapter-2.html",
    3.0: "https://tu-shu-guan.blogspot.com/2006/02/demon-child-chapter-3.html",
    4.0: "https://tu-shu-guan.blogspot.com/2006/02/demon-child-chapter-4.html",
    5.0: "https://tu-shu-guan.blogspot.com/2006/03/demon-child-chapter-5.html",
    6.0: "https://tu-shu-guan.blogspot.com/2006/07/demon-child-chapter-6.html",
    7.0: "https://tu-shu-guan.blogspot.com/2006/09/demon-child-chapter-7.html",
    8.0: "https://tu-shu-guan.blogspot.com/2007/01/demon-child-chapter-8.html",
    9.0: "https://tu-shu-guan.blogspot.com/2007/07/demon-child-chapter-9.html",
    10.0: "https://tu-shu-guan.blogspot.com/2007/07/demon-child-chapter-10.html",
    11.0: "https://tu-shu-guan.blogspot.com/2007/08/demon-child-chapter-11.html",
    12.0: "https://tu-shu-guan.blogspot.com/2007/08/demon-child-commentary.html",
    13.0: "https://tu-shu-guan.blogspot.com/2005/06/demon-child-glossary.html",
}

title = "Demon Child"
author = "Fuyumi Ono"
epub_name = f"{title} - {author}.epub"
cover_img_path = TwelveKingdomsScraper.fetch_and_save_img(
    "https://lh3.googleusercontent.com/_4ORonPYBrqQ/Tb-gZKVXogI/AAAAAAAAAFc/-7tdnOJaLYw/s800/jkcover00.jpg"
)

scraper = TwelveKingdomsScraper(
    title=title,
    author=author,
    cover_img_path=cover_img_path,
    blog_map=blog_map,
    epub_name=epub_name,
)

scraper.run()
