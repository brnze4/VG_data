from path_create_class import download_path
from gen_dl import open_webpage, download
from concurrent.futures import ThreadPoolExecutor as executor
import string

class imgbox_links:
    def __init__(self, url):
        self.url = url
        self.open_webpage = open_webpage
        self.workers = 5
        self.links = self.get_links_from_vg_url() if self.url.find('vipergirls') != -1 else None
        self.convert_page_to_jpg_link()
        
    def get_links_from_vg_url(self):
        self.page = self.open_webpage(self.url, method = 'soup')
        self.soup = self.page.soup if self.page.check_response_code() else None
        if self.soup != None:
            self.links = [item.get('href') for item in self.soup.find_all('a') if item.get('href') != None and item.get('href').find('imgbox') != -1]
        print(self.links)
        return self.links
        
    def convert_page_to_jpg_link(self):
        self.images = []
        for item in self.links:
            self.images.append(convert_link_to_img(item))
    # needs work, specifically, selenium to access the click through to modify links for download        
    # def get_images(self):
    #     with executor(max_workers = self.workers) as exe:
    #         self.results = exe.map(download, self.links)


class convert_link_to_img:
    def __init__(self,url):
        self.url = url
        self.page = open_webpage(self.url, method = 'soup')
        self.link = [item.get('src') for item in self.page.soup.find_all('img') if item.get('src').find('.JPG') != -1 or item.get('src').find('.jpg') != -1]
        self.link = self.link[0] if self.link[0].find('imgbox') != -1 else None
