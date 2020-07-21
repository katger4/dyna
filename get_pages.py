import dyna_fxn as df
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

# base_url = 'http://digital.nypl.org/schomburg/writers_aa19/'
base_url = input('Enter the base url for this site: ')

# page_ids = ['bio2.html','intro.html']
n = int(input("Enter number of frames to pull html from: ")) 
print("Now enter the end of each frame's url followed by enter: ")
page_ids = [input() for i in range(0, n)] 

# out_dir = './data/sch/'
out_dir = input("Enter the path to the directory to write your files to: ")

# get the html for each page
for p in tqdm(page_ids, ncols=70, position=0, leave=True):
    this_base = base_url+p
    if not p.endswith('.html'):
        p+='.html'
    with open(out_dir+p, 'w') as out_file:
        page_text = requests.get(this_base).text
        content_to_extract = df.get_content_to_extract(page_text)
        tree = BeautifulSoup(content_to_extract, 'lxml')
        df.remove_links_and_img(tree)
        out_file.write(str(tree))