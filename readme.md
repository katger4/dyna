# dyna

Let's get some html from Dynaweb and convert it into word documents.

## Requirements

- [python 3](https://www.python.org/downloads/)
	- the [requests](https://requests.readthedocs.io/en/master/) library to access Dynaweb data
	- the [tqdm](https://github.com/tqdm/tqdm) library for progress bars
	- [BeautifulSoup 4](https://pypi.org/project/beautifulsoup4/) for web scraping
- [pandoc](https://pandoc.org/) for html to docx file conversion

## Getting started

Dynaweb pages can come in many shapes and sizes. I'm providing a few different examples here that I hope will be useful when gathering data from similar sites in the future. 

First, take a look at the structure of your site. Most of the dynaweb pages that I've encountered have been organized into [frames](https://www.w3.org/TR/html401/present/frames.html) - for full books, I found it easiest to find the URL for each book or chapter in a book by examining the Table of Contents (identified by `@Generic__BookTocView` in the URL) or collection view (identified by `@Generic__CollectionView` in the URL). In other cases you'll just need a few discrete pages, which is a bit more straightforward, so we'll start there.  

### A few discrete pages

This scenario applies if you have a small number of pages that share a base URL and don't have any internal links or images you'd like to preserve. 

For example - the African American Women Writers of the 19th Century [Introduction](http://digital.nypl.org/schomburg/writers_aa19/intro.html) and [Biographies](http://digital.nypl.org/schomburg/writers_aa19/bio2.html) pages. 

- Both pages share the base URL: `http://digital.nypl.org/schomburg/writers_aa19/`
- Each page has a unique identifier (the tail of the URL for the page): `intro.html` and `bio2.html`

Run ```python3 get_pages.py``` and follow the prompts to extract the data for each page, remove all links and images, and write each page to an html file in a directory. 

Now, change to the directory where you've written your html files to. 

Enter the following command to use pandoc to convert all html files in this directory:
```for f in *.html; do pandoc "$f" -o "${f%.html}.docx"; done```

Magic. :sparkles:

### Getting many pages from a table of contents

Let's say instead of a few pages, you're going to need many (~50). You might also have pages that have sub-pages (perhaps there's a better word...) nested within them. 

For example - the [Mapleson Cylinders](http://digilib.nypl.org/dynaweb/millennium/mapleson/) site is organized with the [Table of Contents](http://digilib.nypl.org/dynaweb/millennium/mapleson/@Generic__BookTocView) frame on the left and the content frames on the right (e.g. [Gounod: FAUST](http://digilib.nypl.org/dynaweb/millennium/mapleson/@Generic__BookTextView/3763)). 

Rather than clicking on each frame and copy-pasting its page identifier (for "Gounod: FAUST" - 3763), use the function `get_page_ids_from_toc` from the `dyna_fxn.py` file to pass in the base URL `http://digilib.nypl.org/dynaweb/millennium/mapleson/` and get a list of page IDs from each heading returned (in Table of Contents order).

Next, pass this list to the `get_frames_with_links` function, along with the base URL, and the directory where you'd like your html files to be written to. One file will be written for each heading in the table of contents. This function also replaces links to sub-pages with the content from those sub-pages. If the page doesn't have any nested sub-pages, this section will be ignored but still run.

For example, the page [Meyerbeer: LES HUGUENOTS](http://digilib.nypl.org/dynaweb/millennium/mapleson/@Generic__BookTextView/5678) has 8 sub-pages. If you get the raw text for this page using requests (e.g. `requests.get('http://digilib.nypl.org/dynaweb/millennium/mapleson/@Generic__BookTextView/5678').text`), you could see that the content for this page is followed by another table of contents with links to those sub-pages:

 ```
 ...
 <HR>
      <br><h3 align=center> Meyerbeer: LES HUGUENOTS </h3><p> In 1896, Maurice Grau offered Metropolitan Opera audiences, at
				advanced prices (a seven-dollar top), performances of <i> Les
				Huguenots </i> that he billed as "Nights of the Seven Stars"; the stars of the
				first one were Lillian Nordica (Valentine), Nellie Melba (Marguerite De
				Valois), Sofia Scalchi (Urbain), Jean De Reszke (Raoul), his brother Edouard
				(Marcel), Pol Plançon (St. Bris), and Victor Maurel (Nevers). Such
				casting for Meyerbeer's historical epic remained a Met specialty even into the
				years when Mapleson was recording, and at least three of the original "Seven
				Stars" turn up on the cylinders from <i> Huguenots. </i> In the
				three seasons from 1900-03, the opera was performed four, three, and
				three times respectively--and, as the cylinders indicate, the language in
				which the principals sang alternated between the original French and Italian
				translation, presumably dependent on the casting (the chorus always sang in
				Italian). 
      <p><TABLE CELLPADDING=0 BORDER=0 WIDTH=898>
  <TR>
    <TD WIDTH=40>
    <TD WIDTH=10>
    <TD ALIGN=LEFT VALIGN=TOP WIDTH=800 NOWRAP>
        <A HREF="@Generic__BookTextView/5694#X">  <font size=2> 				  				   Band 1 
				  
				 </font> </A>
  </TR>
</TABLE><TABLE CELLPADDING=0 BORDER=0 WIDTH=898>
  <TR>
    <TD WIDTH=40>
    <TD WIDTH=10>
    <TD ALIGN=LEFT VALIGN=TOP WIDTH=800 NOWRAP>
        <A HREF="@Generic__BookTextView/5838#X">  <font size=2> 				  				   Band 2 
				  
				 </font> </A>
  </TR>
  ...
  ``` 

Rather than remove those links, we need to replace them with the content from those sub-pages, which we can do with BeautifulSoup `replace_with()`. This is probably bad practice if we cared about making very well-formed html, but so far, BeautifulSoup and pandoc have both worked well together to get around any html weirdness and give us the documents we need. 

Once you've written all your html files with `get_frames_with_links`, change to that directory and enter the same command as above:
```for f in *.html; do pandoc "$f" -o "${f%.html}.docx"; done```

### Getting a collection of books (and each section in those books)

For one more layer of complexity, let's look at an example where instead of a single table of contents, you have a collection of books, each with its own table of contents. The goal here is to identify each book, get its table of contents, and compile all of its pages into one big html file.

The books in the African American Women Writers of the 19th Century collection are listed on the page `http://digilib.nypl.org/dynaweb/digs/@Generic__CollectionView`. The function `get_book_tocs` from the `dyna_fxn.py` file will output a list of book page IDs in the order they were listed on the collection view page (use the base URL `http://digilib.nypl.org/dynaweb/digs/` here). 

Next, for each book, get the list of chapters/pages in that book using the `get_page_ids_from_toc` function, the base URL listed above, and that book's page ID. 

For each book and its list of page IDs, use the function `compile_book_pages` to write a single html file per book, replacing any sub-page links with the content from those pages. 

Finally, change to the directory with the book html files and enter the same command as above:
```for f in *.html; do pandoc "$f" -o "${f%.html}.docx"; done```

## A note on frames

I've had more success using Chrome to view dynaweb pages organized into frames. Firefox didn't work as well for me. If you want to see a particular frame's source code, use the "View Frame Source" option when right-clicking on a frame. 

Good luck!
