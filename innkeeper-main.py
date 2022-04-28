from typing import Dict, List, Optional
from scraper import Scraper

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
}

title = "Innkeeper Chronicles - Sweep of the Heart"
author = "Ilona Andrews"
cover_img_path = "images/A-dahl-cover-art-chop.jpg"
epub_name = "Sweep of the Heart.epub"

scraper = Scraper(
    title=title,
    author=author,
    cover_img_path=cover_img_path,
    blog_map=blog_map,
    epub_name=epub_name,
)

scraper.run()
