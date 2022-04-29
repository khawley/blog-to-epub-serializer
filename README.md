# Blog to Epub Serializer

This project uses the [epublib](https://docs.sourcefabric.org/projects/ebooklib/en/latest/) and [beautifulsoup](https://beautiful-soup-4.readthedocs.io/en/latest/) libraries to collect and parse serial blog posts into epubs.

It is written for python 3.9+.

## Layout
### blog_to_epub_serializer
Contains the complex logic of splitting and creating an epub.  Users should start with `scraper.Sraper` and create a child class.  This child class should at a bare minimum implement `parse_chapter_text` which will finesse the html soup (isolate the article text, remove images you don't want, social media footers, etc).

### serializers
Some previous examples can be seen here.  Each creates a different epub from a different blog series source.  

`innkeeper` supports an image at the start of each chapter, but parses out the wordpress filler images.

`seaofthewind` includes a copyright page (citing the blog source and original source material), an additional volume cover, and maps.

## Getting started
Using the virtual environment tools of your choice, install the python dependencies in `requirements.txt`.

It is recommended, but not required that you also install the `requirements-dev.txt`.  If you intend to contribute to the project, please be sure to install these.

### Using virtualenv

```bash
virtualenv -p python3 venv
```

Then activate the enviroment anytime you wish to work on the project.

```bash
. venv/bin/activate
```

Install the dependencies.
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Write your own Serializer

I recommend perusing the examples to get you started.  Below are some examples with explanations.

### Basic Example
```python
# example basic serializer
from blog_to_epub_serializer.book_utils import Chapter
from blog_to_epub_serializer.scraper import Scraper


class MyScraper(Scraper):
    
    def parse_chapter_text(
        self, soup, chapter_idx
    ):
        # you will write the beautifulsoup code to isolate the chapter text
        # this assumes that each blog post uses the same format:
        # elements, class names, header, footers.
        # This allows you to standardize the parsing across multiple posts
        
        # You will parse this from the html. 
        # This will appear in the Table of Contents, and be added automatically
        # as an h1 at the top of the Chapter text
        title = ""
        
        # The parsed and cleaned up soup you want written to the epub
        html_content = ""  
        
        return Chapter(
            idx=chapter_idx, title=title, html_content=html_content,
        )
    

# This dictionary will map the chapter numbers to url's
blog_map = {
    # the keys here can be any float. They are used for ordering and will 
    # appear in the hidden epub contents
    # They are not reflected in the chapter title
    0.5: "https://example.com/prologue",
    1.0: "https://example.com/chapter-1",
}

# Setup the metadata for the class
my_scraper = MyScraper(
    title="My book",
    author="An Author",
    blog_map=blog_map,
    
    # the file name that will be written into the local_cache
    epub_name="my_book.epub",  
    
    # should be a local path not a url
    cover_img_path="local_cache/cropped_cover.jpg"  
)

# Start the scraper. By default it will save to local cache, 
# and use that on reruns
my_scraper.run()

# To instead force the Scraper to download fresh files with each run
my_scraper.run(use_cache=False)
```

### Example - Chapters with Images
```python
# serializer for chapters with images
from blog_to_epub_serializer.book_utils import Chapter
from blog_to_epub_serializer.scraper import Scraper


class MyScraper(Scraper):
    
    def parse_chapter_text(self, soup, chapter_idx):
        title = "..."
        html_content = "..."
        
        # for parsing images, you will need to isolate their src url 
        # and download them
        local_images = []
        images = soup.findAll("img")
        for image in images:
            # find the url src (ould be in "data-src" or another attr)
            source = image.attrs['src']
            
            # this will download and save the image to the local_cache
            local_src = self.fetch_and_save_img(source, chapter_idx)
            
            # be sure to update the html image's source to point to the new 
            # local path
            image.attrs['src'] = local_src
            
            local_images.append(local_src)
        
        
        return Chapter(
            idx=chapter_idx, title=title, html_content=html_content,
            # include the locally saved images
            image_paths=local_images,
        )
```

#### Saving the cover image from url

The same method can be used to save a copy of the cover image as well.

```python
# download and save the cover to local_cache
cover_img_path = Scraper.fetch_and_save_img("http://example.com/cover.jpg")

my_scraper = MyScraper(
    title="My book",
    author="An Author",
    blog_map=blog_map,
    epub_name="my_book.epub", 
    cover_img_path=cover_img_path
)
```

### Example - Add custom preface chapters

You may wish to add a copyright page, or add maps or illustrations to the beginning of the book.  This shows how to augment the Scraper to do that.

```python
# serializer with custom preface
from typing import List, Optional
from blog_to_epub_serializer.book_utils import Chapter
from blog_to_epub_serializer.scraper import Scraper

class MyScraper(Scraper):
    
    def parse_chapter_text(self, soup, chapter_idx):
        ...
        pass
    
    def add_preface_chapters(self) -> Optional[List[Chapter]]:
        # this is an optional method that returns None in the base, but will 
        # insert any returned Chapters before the first
        return [self.add_copyright()] + self.add_maps()
    
    # these are custom functions added just for this Scraper.  
    # They don't exist in the base class
    def add_copyright(self) -> Chapter:
        html_content = f"""
            <h1>{self.title}</h1>
            <p>Published 2022</p>
        """
        return Chapter(
            idx="0.1",
            title="Copyright",
            html_content=html_content,
            
            # When this is true, there is no added h1 tag that comes from 
            # the `title` kwarg
            no_title_header=True,
        )
    
    def add_maps(self) -> List[Chapter]:
        map1_img = self.fetch_and_save_img("http://example.com/map1.jpg")
        map1_content = f"<img src='{map1_img}'>"
        map1_chapter = Chapter(
            idx=0.2,
            title="Map 1",
            html_content=map1_content,
            image_paths=[map1_img],
            no_title_header=False,
        )
        
        map2_img = self.fetch_and_save_img("http://example.com/map1.jpg")
        map2_content = f"<img src='{map2_img}'>"
        map2_chapter = Chapter(
            idx=0.3,
            title="Map 2",
            html_content=map2_content,
            image_paths=[map1_img],
            no_title_header=False,
        )
        return [map1_chapter, map2_chapter]
```

## Run your Serializer

The resources are written with the assumption that you are invoking the script
from the repo base.  To run some of the committed serializers:

```bash
# from Repo Base

# activate/switch into your virtualenv and run:
python serializers/innkeeper.py
```
