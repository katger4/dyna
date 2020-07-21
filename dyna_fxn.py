import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

def get_content_to_extract(page_text):
    if page_text.count('<HR>') == 2:
        # most pages have two of these section break tags, with the content we want in the middle
        return page_text.split('<HR>')[1]
    elif page_text.count('<HR') == 1:
        # others have one section break at the end of the page
        return page_text.split('<HR')[0]
    else:
        # there are probably other styles out there, for now just return the whole page
        return page_text

def remove_links_and_img(tree):
    # remove links (internal links, will be broken anyways)
    if len(tree.find_all('a')) > 0:
        for a in tree('a'):
            a.decompose()
    # remove images (we don't have those files anyways)
    if len(tree.find_all('img')) > 0:
        for img in tree("img"):
            img.decompose()

def replace_link_with_content(tree, p, base_url):
    for a in tree.find_all('a', href=True):
        if a['href'].startswith('@Generic__BookTextView') and p not in a['href']:
            linked_content = requests.get(base_url+a['href'].split(';')[0]).text
            content_to_extract = get_content_to_extract(linked_content)
            linked_tree = BeautifulSoup(content_to_extract, 'lxml')
            a.replace_with(linked_tree)

def get_page_ids_from_toc(base_url, book_id=''):
    #base_url = 'http://digilib.nypl.org/dynaweb/millennium/mapleson/'
    #base_url = 'http://digilib.nypl.org/dynaweb/digs/'
    #book_id = 'wwm972'
    page_ids = []
    toc = requests.get(base_url+book_id+'@Generic__BookTocView').text
    soup = BeautifulSoup(toc, 'lxml')
    links = soup.find_all('a', href=True)
    for link in links:
        if link['href'].startswith('@Generic__BookTextView/'):
            pid = link['href'].split('@Generic__BookTextView/')[-1].split('#')[0]
            page_ids.append(pid)
    return page_ids

def get_frames_with_links(base_url, page_ids, out_dir):
    for p in tqdm(page_ids, ncols=70, position=0, leave=True):
        this_base = base_url+'@Generic__BookTextView/'+p
        if not p.endswith('.html'):
            p+='.html'
        with open(out_dir+p, 'w') as out_file:
            page_text = requests.get(this_base).text
            content_to_extract = get_content_to_extract(page_text)
            tree = BeautifulSoup(content_to_extract, 'lxml')
            replace_link_with_content(tree, p, base_url)
            remove_links_and_img(tree)
            out_file.write(str(tree))

def get_book_tocs(base_url):
    #base_url = 'http://digilib.nypl.org/dynaweb/digs/'
    book_tocs = []
    toc = requests.get(base_url+'@Generic__CollectionView').text
    soup = BeautifulSoup(toc, 'lxml')
    links = soup.find_all('a', href=True)
    for link in links:
        if link['href'].startswith('/dynaweb/digs/'):
            pid = link['href'].replace('/dynaweb/digs/','').replace('@Generic__BookView','')
            book_tocs.append(pid)
    return book_tocs

def compile_book_pages(base_url, book_id, page_ids, out_dir):
    fname = book_id[:-1]+'.html'
    with open(out_dir+fname, 'w') as out_file:
        for p in tqdm(page_ids, ncols=70, position=0, leave=True):
            this_base = base_url+book_id+'@Generic__BookTextView/'+p
            page_text = requests.get(this_base).text
            content_to_extract = get_content_to_extract(page_text)
            tree = BeautifulSoup(content_to_extract, 'lxml')
            replace_link_with_content(tree, p, base_url)
            remove_links_and_img(tree)
            out_file.write(str(tree))
