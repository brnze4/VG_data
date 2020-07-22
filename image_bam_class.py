from path_create_class import download_path
from gen_dl import open_webpage, download
from concurrent.futures import ThreadPoolExecutor as executor

class Image_Bam:
    def __init__(self, url):
        self.url = url
        self.path = download_path()
        self.open_webpage = open_webpage
        self.workers = 5
        
    def get_links(self):
        self.page = self.open_webpage(self.url, method = 'soup')
        self.soup = self.page.soup if self.page.good_response() else None
        self.links = [[item.get('src'), self.path.save_path] for item in self.soup.find_all('img') if item.get('src').find('imagebam') != -1]
        
# needs work, specifically, selenium to access the click through to modify links for download        
    def get_images(self):
        with executor(max_workers = self.workers) as exe:
            self.results = exe.map(download, self.links)
        
