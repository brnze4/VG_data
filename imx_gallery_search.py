'''
This class will ask
    What gallery to search
    Should previews be downloaded
    Should link files be created
'''
import os
import time
import string
import tkinter
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from tkinter import filedialog
from random import randrange as random
from concurrent.futures import ThreadPoolExecutor

class Imx_gallery_search:
    def __init__(self, 
                 thread_executor = None,
                 auto_search = True,
                 child = False,
                 rootPath = '',
                 search_type = 'normal', 
                 search_speed = 'fast', 
                 directory = '', 
                 series = '',
                 gallery = '',
                 index = ''):
        
        # print(f'new instantce\tdirectory {directory}\tseries {series}\tType {search_type}')
        self.search_speed = search_speed.lower()
        self.search_type = search_type.lower().strip()
        self.rootPath = rootPath
        if search_type == 'deep':
            self.start_deep_search()
        else:
            self.directory = directory
            self.series = series
            self.gallery = gallery
            self.index = index
            self.gallery_search_list = []
            self.exe = ThreadPoolExecutor(max_workers = 5)  if thread_executor == None else thread_executor
            self.create_reference_list()
            self.auto_search = auto_search
            self.start_auto_search()
            
    def start_deep_search(self):
        self.create_reference_list()
        self.ask_for_inputs()
        self.create_deep_list_to_search()
        
        
    def get_root_path(self):
        if self.rootPath == None or self.rootPath == '':
            root = tkinter.Tk()
            self.rootPath = filedialog.askdirectory().replace('/', '\\')
            # print(self.rootPath)
            root.withdraw()
        
        
    def ask_for_inputs(self):
        if self.search_type != 'full':
            self.directory = input("Galleries are 4 digits long, WD40, for example.\nPlease specifiy the first letter/number, \'_\' for a 3 digit search: ")
            if self.search_type != 'deep':
                self.series = input('Now the second index please: ')
                if self.search_type == 'shallow':
                    self.gallery = input('Third index please: ')
                    print(f'Searching galleries {self.directory}{self.series}00 to {self.directory}{self.series}ZZ')
   
    def create_reference_list(self):
        self.reference_list = string.digits + string.ascii_lowercase
        self.hex_ref_list = self.reference_list[0:16]
        return (self.reference_list, self.hex_ref_list)
   
    def create_shallow_list_to_search(self):
        # print('shallow')
        for i in self.reference_list:
            self.gallery_search_list.append(self.directory+self.series+self.gallery+i)
    
    def create_normal_list_to_search(self):
        print('create list normal')
        for i in self.reference_list:
            self.gallery = i
            self.create_shallow_list_to_search()
            
    def create_deep_list_to_search(self):
        print('create list deep')
        for i in self.reference_list:
            self.series = i
            self.gallery_search = Imx_gallery_search(exe,
                                                     rootPath = self.rootPath,
                                                     directory = self.directory,
                                                     series = self.series,
                                                     search_type = 'normal',
                                                     search_speed = 'fast')
            
    def create_full_list_to_search(self):
        # print('create list full')
        for i in self.reference_list:
            self.directory = i
            self.create_deep_list_to_search()
    
    def create_search_list(self):
        if self.search_type == 'full':
            self.create_full_list_to_search()
        elif self.search_type == 'deep':
            self.create_deep_list_to_search()
        elif self.search_type == 'normal':
            self.create_normal_list_to_search()
        elif self.search_type == 'shallow':
            self.create_normal_list_to_search()
        else:
            print('SearchType unspecified')
            raise SystemExit
    
    def search_galleries(self):
        if self.search_speed == 'fast':
            self.list_of_galleries_checked = [self.exe.submit(check_single_IMX_gallery,
                                              galleryID = galleryID,
                                              rootPath = self.rootPath) for galleryID 
                                              in self.gallery_search_list]
        else:
            for gallery in self.gallery_search_list:
                check_single_IMX_gallery(gallery, self.rootPath)
                  
    def start_auto_search(self):
        # print('start auto')
        self.get_root_path()
        if self.directory == '':
            # print(f'Direct {self.directory}')
            self.ask_for_inputs() 
        self.create_search_list()
        if self.auto_search:
            # print('searching')
            self.search_galleries()
            self.auto_search = False
            
    def change_inputs(self):
        self.ask_for_inputs()
        
    def start_search(self):
        # print('start_search')
        self.auto_search = True
        self.start_auto_search()
    
        
        
class check_single_IMX_gallery:
    def __init__(self, 
                 galleryID = None, 
                 rootPath = None,
                 auto_search = True):
        # print('single gallery')
        self.start_time = time.perf_counter()
        self.galleryID = galleryID
        self.saveLocation = rootPath
        self.directory = galleryID[0]
        self.series = galleryID[1]
        self.url = f'https://imx.to/g/{self.galleryID}'
        self.preview_url = ''
        self.path = os.getcwd() if rootPath == None else rootPath
        self.list_of_images = None
        self.number_of_images = None
        self.minimum_number = 25
        self.response = None
        self.good_response = None
        self.soup = None
        self.number_of_images = None
        self.preview_url = None
        self.auto_search = auto_search
        self.fix_inputs_from_threads()
        self.go_search()
     
    def fix_inputs_from_threads(self):
        # print(type(self.galleryID))
        if type(self.galleryID) == list:
            self.galleryID, self.path, self.auto_search = self.galleryID
            self.url = f'https://imx.to/g/{self.galleryID}'
            self.directory = self.galleryID[0]
            self.series = self.galleryID[1]
        
    def check_galleryID_valid(self):
        if len(self.galleryID) >= 2 and len(self.galleryID) <= 4:
            if self.galleryID[0] == '' or self.galleryID[1] == '':
               pass
               
    def load_gallery_page(self):
        self.response = requests.get(self.url)
        
    def check_response_code(self):
        sleep = 30/random(10,100)
        self.good_response = False
        if self.response.status_code == 503:
            time.sleep(sleep)
            print(f'Server Error {self.response.status_code}: Attempting to load gallery {self.url} again in {sleep} seconds.')
            self.save_preview_image()
        elif self.response.status_code == 404:
            print(f'404, sleeping {sleep} seconds')
            time.sleep(sleep)
        elif self.response.status_code >= 400 and self.response.status_code < 500:
            if self.soup == None:
                print(f'Error: IMX gallery {self.galleryID} responsed {self.response.status_code}, gallery not retreived.')
            elif self.preview_url != None:
                print(f'Error: Unable to retrieve gallery {self.galleryID} preview image.  Server responded {self.response.status_code}')
            time.sleep(sleep)
        else:
            self.good_response = True
        return self.good_response
            
    def make_soup_object(self):
        self.soup = BeautifulSoup(self.response.text, 'html.parser') if self.good_response else None
        
    def make_list_of_images(self):
        self.list_of_images = [item.get('src') for 
                               item in self.soup.find_all('img') if 
                               item.get('class') != None and 
                               item.get('class')[0] == 'imgtooltip']
        self.number_of_images = len(self.list_of_images)
        
    def save_gallery_details(self):
        with open(f'{self.path}\\{self.galleryID}_{self.number_of_images}.txt', 'w') as file:
            file.write(f'{self.number_of_images} Images in Gallery.\n\n')
            file.write(f'Links to Thumbnail images\n')
            file.writelines(str(item) +'\n' for item in self.list_of_images)
    
    def create_path(self):
        self.save_path = f'{self.saveLocation}\\Previews\\{self.directory}\\{self.series}'
        # print(f' path {self.save_path} {os.path.exists(self.save_path)}')
        if os.path.exists(f'{self.saveLocation}\\Previews\\{self.directory}\\{self.series}'):
            self.path = f'{self.saveLocation}\\Previews\\{self.directory}\\{self.series}'
            pass
        else:
            try:
                os.makedirs(f'{self.saveLocation}\\Previews\\{self.directory}\\{self.series}')
            except FileExistsError:
                self.path = f'{self.saveLocation}\\Previews\\{self.directory}\\{self.series}'
            except:
                print(f'Something went wrong with the save path {self.save_path}, quitting.')
                raise SystemExit
            
    def save_preview_image(self):
        self.url = self.list_of_images[0] if self.number_of_images != None else None
        if self.url != None:
            self.load_gallery_page()
            self.check_response_code()
            # print(self.response.status_code)
            
            if self.good_response:
                # print('saving picture')
                self.title = self.soup.title.text.split(' / ')[-1]
                try:
                    with open(f'{self.path}\\{self.galleryID} {self.title}.jpg', 'wb') as image:
                        image.write(self.response.content)
                    # print(self.response.content)
                except TypeError:
                    print(f'Error: Unable to save gallery {self.galleryID} preview image.  Data in self.response.content is not Bytes')
            
        else:
            print(f'Unable to download Gallery {self.galleryID} preview.  Number of images found in gallery: {self.number_of_images}')
        
    def go_search(self):
        if self.galleryID != None and self.auto_search:
            # print(self.path, self.galleryID, self.url)
            self.fix_inputs_from_threads()
            self.load_gallery_page()
            if self.check_response_code() == True:
                self.make_soup_object()
            if self.soup != None:
                self.make_list_of_images() 
            if self.number_of_images != None and self.number_of_images > self.minimum_number:
                self.create_path()
                self.save_gallery_details()
                self.save_preview_image()
            # print(f'done, performance {time.perf_counter()-self.start_time}')
            self.auto_search = False
        else:
            print(f'Can\'t search, galleryID is wrong.  Input is {self.galleryID}')
            
    def is_good_gallery(self):
        if self.number_of_images > 10:
            # print('good gallery')
            return True
        
if __name__ == '__main__':
    t1 = time.perf_counter()
    exe = ThreadPoolExecutor(max_workers = 5)
    path = 'z:\\Pictures'
    results = Imx_gallery_search(exe, rootPath = path, auto_search = True, search_type = 'deep')
    exe.shutdown(wait = True)
    print(time.perf_counter()-t1)
