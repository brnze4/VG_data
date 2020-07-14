import string
import os
import time
from random import randrange as random
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog
from tqdm import tqdm
import tkinter
import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# This class will ONLY download a gallery specified.  It should ask for
# a save location for each instantiation.  Possibly through a GUI

class imx_crawl:
    
    def __init__(self, url, rootPath, executor = None):
        self.exe = executor
        # print('exe')
        self.rootPath = rootPath
        # print(self.rootPath)
        self.crawl_path = '\\'.join([self.rootPath, 'crawl'])
        # print(self.crawl_path)
        self.start_url = url.replace('u/t', 'i')
        # print(self.start_url)
        self.make_crawl_root()
        # print(self.crawl_root)
        self.create_reference_list()
        # print('ref list')
        self.create_crawl_list_to_search()
        # print(self.crawl_search_list[0:10])
        self.crawl_path = '\\'.join([self.crawl_path, self.crawl_search_list[0].split('/')[-1].split('.')[0]])
        # print(self.crawl_path)
        self.make_directory()
        # print(os.path.exists(self.crawl_path))
        self.crawl_with_threads()
        
    def make_directory(self):
        try:
            os.makedirs(self.crawl_path)
        except FileExistsError:
            pass
        except:
            print('It\'s broke...')
            raise SystemExit
        
    def get_root_path(self):
        if self.rootPath == None:
            root = tkinter.Tk()
            self.rootPath = filedialog.askdirectory().replace('/', '\\')
            # print(self.rootPath)
            root.withdraw()
            
    def create_crawl_list_to_search(self):
        self.crawl_search_list = []
        for i in self.reference_list:
            for j in self.reference_list:
                self.crawl_search_list.append(self.crawl_root + i + j + '.jpg')
                
    def make_crawl_root(self):
        self.crawl_root = self.start_url.split('.jpg')[0][0:-2]
         
    def create_reference_list(self):
        self.reference_list = string.digits + string.ascii_lowercase
        self.hex_ref_list = self.reference_list[0:16]
    
    def crawl_with_threads(self):
        with open(self.crawl_path+'\\'+ 'source.txt', 'w') as f:
                  f.write(self.start_url)
        print(self.crawl_search_list)
        self.exe_results = [self.exe.submit(Imx_download, url, self.crawl_path) for url in tqdm(self.crawl_search_list[150:])]
   
class Imx_download:
    def __init__(self, url, path):
        # print(f'dl {url}')
        self.url = url
        self.path = path
        self.index = self.url.split('/')[-1]
        self.file_path = '\\'.join([self.path, self.index])
        # print('opening page')
        self.page = open_webpage(self.url)
        # print(f'started {url}\t {path}\tResponse: {self.page.response}')
        # self.data = self.page.image if self.page.good_response else ''
        # print(self.url, self.path, self.file_path, self.page.response, self.index)
        self.save_image()
        
    def save_image(self):
        retVal = 'Bad Image'
        # print(len(self.page.response.content))
        if self.page.good_response:
            with open(self.file_path, 'wb') as fb:
                      fb.write(self.page.response.content)
            retVal == 'Saved'
        return retVal

class open_webpage:
    def __init__(self, url):
        self.url = url
        self.get_content()
            
    def load_gallery_page(self):
        self.response = requests.get(self.url)
        
    def make_soup_object(self):
        self.soup = BeautifulSoup(self.response.text, 'html.parser') if self.good_response else None
        
    def check_response_code(self):
        sleep = 30/random(10,100)
        self.good_response = False
        if self.response.status_code == 503:
            time.sleep(sleep)
            print(f'Server Error {self.response.status_code}: Attempting to load gallery {self.url} again in {sleep} seconds.')
            self.get_content()
        elif self.response.status_code == 404:
            print(f'404, sleeping {sleep} seconds')
            time.sleep(sleep)
        elif self.response.status_code >= 400 and self.response.status_code < 500:
            if self.soup == None:
                print(f'Error: IMX gallery {self.url} responsed {self.response.status_code}, gallery not retreived.')
            elif self.preview_url != None:
                print(f'Error: Unable to retrieve gallery {self.url} preview image.  Server responded {self.response.status_code}')
        else:
            self.good_response = True
        return self.good_response
    
    def make_soup(self):
       self.load_gallery_page()
       if self.check_response_code():
          self.make_soup_object()

    def get_content(self):
        self.load_gallery_page()
        # print(f'response: {self.response}')
        if self.check_response_code():
            self.image = self.response.content
# class download_path():
#     def __init__(self, rootPath, galleryID): #rootPath should be like z:\Pictures
#         self.rootPath = rootPath
#         self.galleryID = galleryID.upper()
#         self.save_path = ''
#         self.folder = ''
#         self.do_it()
        
#     def get_parent_folder(self):
#         root = tkinter.Tk()
#         self.save_path = filedialog.askdirectory().replace('/', '\\')
#         self.folder = os.path.split(self.save_path)[-1]
#         root.destroy()
    
#     def create_path(self):
#         if not os.path.exists(f'{self.save_path}\\{self.galleryID}'):
#             try:
#                 os.makedirs(f'{self.save_path}\\{self.galleryID}')
#                 self.save_path = f'{self.save_path}\\{self.galleryID}'
#             except:
#                 print(f'Failed to make path {self.save_path}\\{self.galleryID}\nExiting')
#                 raise SystemExit
                
#     def do_it(self):
#         self.get_parent_folder()
#         self.create_path()

if __name__ == '__main__':
    url = input('URL: ')
    exe = ThreadPoolExecutor(max_workers=5)
    rootPath = 'z:\\Pictures'
    dl = imx_crawl(url, rootPath, exe)
    exe.shutdown(wait = True)
