import os
import time
import tkinter
import requests
from bs4 import BeautifulSoup
from tkinter import filedialog
from random import randrange as random
from concurrent.futures import ThreadPoolExecutor

class retrieve_imx_gallery():
    def __init__(self, galleryID=None, rootPath=None, executor=None):
        self.response = None
        self.soup = None
        self.galleryID = galleryID
        self.list_of_images = None
        self.number_of_images = None
        self.good_response = False
        self.url = f'https://imx.to/g/{galleryID}'
        self.exe = executor
        self.rootPath = rootPath
        self.do_it()
              
    def load_gallery_page(self):
        self.response = requests.get(self.url)
        
    def check_galleryID_valid(self):
        if len(self.galleryID) >= 2 and len(self.galleryID) <= 4:
            if self.galleryID[0] == '' or self.galleryID[1] == '':
               pass
            
    def make_soup_object(self):
        self.soup = BeautifulSoup(self.response.text, 'html.parser') if self.good_response else None
        
    def make_list_of_images(self):
        self.list_of_images = [item.get('src') for 
                               item in self.soup.find_all('img') if 
                               item.get('class') != None and 
                               item.get('class')[0] == 'imgtooltip']
        self.number_of_images = len(self.list_of_images)
        
    def check_response_code(self):
        self.good_response = False
        if self.response.status_code == 503:
            print(f'Server Error {self.response.status_code}: Attempting to load gallery {self.galleryID} again.')
            time.sleep(random(1,7))
            self.save_preview_image()
        elif self.response.status_code >= 400 and self.response.status_code < 500:
            if self.soup == None:
                print(f'Error: IMX gallery {self.galleryID} responsed {self.response.status_code}, gallery not retreived.')
            elif self.preview_url != None:
                print(f'Error: Unable to retrieve gallery {self.galleryID} preview image.  Server responded {self.response.status_code}')
        else:
            self.good_response = True
        return self.good_response
    
    def set_gallery_id(self, galleryID = None):
        if galleryID != None:
            self.galleryID = galleryID
            self.url = f'https://imx.to/g/{self.galleryID}'
            
    def get_full_length_lead_in(self):
        self.url = self.list_of_images[0]
        self.load_gallery_page()
        self.full_length_lead_in = '/'.join(self.response.url.split('/')[0:-1]).replace('/t/', '/i/')+'/'
    
    def alter_list_of_images(self):
        self.list_of_images = [self.full_length_lead_in + item.split('/')[-1] for item in self.list_of_images]
    
    def set_url(self, url):
        if url != None:
            self.url = url
            self.galleryID = self.url.split('/')[-1]
            
    def check_executor(self, executor):
        if executor == None:
            self.exe = ThreadPoolExecutor(max_workers = 10)
        else:
            self.exe = executor
            
    def set_path(self):
        self.path = download_path(self.rootPath, self.galleryID).do_it()
        
    
    def do_it(self):
        self.load_gallery_page()
        self.check_response_code()
        if self.good_response:
            self.make_soup_object()
            self.make_list_of_images()
            # print(self.list_of_images[0:3])
            self.get_full_length_lead_in()
            print(self.full_length_lead_in)
            self.alter_list_of_images()
            # print(self.list_of_images[0:3])
            self.path = download_path(self.rootPath, self.galleryID)
            # print(self.path.save_path)
            # print(type(self.exe))
            go_on = ''
            if go_on == '' or go_on == '\n':
                self.exe_results = [self.exe.submit(Imx_download, url, index+1, self.path.save_path) for index, url in enumerate(self.list_of_images)]
            
class open_webpage:
    def __init__(self, url, check_soup = True):
        self.url = url
        self.check_make_soup = check_soup
        self.make_soup()
        
            
    def load_gallery_page(self):
        self.response = requests.get(self.url)
        
    def make_soup_object(self):
        self.soup = BeautifulSoup(self.response.text, 'html.parser') if self.good_response else None
        
    def check_response_code(self):
        sleep = 50/random(10,100)
        self.good_response = False
        if self.response.status_code == 503:
            time.sleep(sleep)
            print(f'Server Error {self.response.status_code}: Attempting to load gallery {self.url} again in {sleep} seconds.')
            self.make_soup()
        elif self.response.status_code == 404:
            print(f'404, sleeping {sleep} seconds')
            time.sleep(sleep)
        elif self.response.status_code >= 400 and self.response.status_code < 500:
            if self.soup == None:
                print(f'Error: IMX gallery {self.galleryID} responsed {self.response.status_code}, gallery not retreived.')
            elif self.preview_url != None:
                print(f'Error: Unable to retrieve gallery {self.galleryID} preview image.  Server responded {self.response.status_code}')
        else:
            self.good_response = True
        return self.good_response
    
    def make_soup(self):
       self.load_gallery_page()
       if self.check_response_code() and self.check_make_soup:
          self.make_soup_object()
       
          

class Imx_download:
    def __init__(self, url, index, path):
        print(f'started picture {index} class')
        self.url = url
        self.path = path
        self.index = str(index)
        self.file_path = '\\'.join([self.path, self.index+'.jpg'])
        self.page = open_webpage(self.url, False)
        self.data = self.page.response.content if self.page.good_response else ''
        # print(self.url, self.path, self.file_path, self.page.response)
        self.save_image()
        
        
        
    def save_image(self):
        print(self.url, self.path, self.file_path)
        with open(self.file_path, 'wb') as fb: 
                fb.write(self.data) 
        return 'Saved'
  
        

class download_path():
    def __init__(self, rootPath, galleryID): #rootPath should be like z:\Pictures
        self.rootPath = rootPath
        self.galleryID = galleryID.upper()
        self.save_path = ''
        self.folder = ''
        self.do_it()
        
    def get_parent_folder(self):
        root = tkinter.Tk()
        self.save_path = filedialog.askdirectory().replace('/', '\\')
        self.folder = os.path.split(self.save_path)[-1]
        # print(f'Folder: {self.folder}')
        root.destroy()
    
    def create_path(self):
        if not os.path.exists(f'{self.save_path}\\{self.galleryID}'):
            try:
                os.makedirs(f'{self.save_path}\\{self.galleryID}')
            except:
                print(f'Failed to make path {self.save_path}\\{self.galleryID}\nExiting')
                raise SystemExit
        self.save_path += '\\'+self.galleryID
        print(f'download_path: {self.save_path}')
        # if input('continue? ') != '':
        #     raise SystemExit
                
    def do_it(self):
        self.get_parent_folder()
        self.create_path()
        
if __name__ == '__main__':
   
    url = input('Gallery: ')
    root = tkinter.Tk()
    rootPath = filedialog.askdirectory().replace('/', '\\')
    root.destroy()
    print(rootPath)
    keep_going = ''
    if keep_going != '' or keep_going != '\n':
        with ThreadPoolExecutor(max_workers = 5) as executor:
            gal = retrieve_imx_gallery(url, rootPath, executor)
