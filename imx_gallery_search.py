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
from bs4 import BeautifulSoup
from tkinter import filedialog
from random import randrange as random
from concurrent.futures import ThreadPoolExecutor

class Imx_gallery_search:
    def __init__(self, thread_executor = None, rootPath = None, auto_search = True):
        self.directory = ''
        self.series = ''
        self.exe = ThreadPoolExecutor(max_workers = 20) if thread_executor == None else thread_executor
        self.create_reference_list()
        self.rootPath = None
        self.auto_search = auto_search
        self.start_auto_search()
        
    def get_root_path(self):
        if self.rootPath == None:
            root = tkinter.Tk()
            self.rootPath = filedialog.askdirectory().replace('/', '\\')
            # print(self.rootPath)
            root.withdraw()
        
        
    def ask_for_inputs(self):
        self.directory = input("Galleries are 4 digits long, WD40, for example.\nPlease specifiy the first index: ")
        self.series = input('Now the second index please: ')
        print('Searching galleries {self.directory}{self.series}00 to {self.directory}{self.series}ZZ')
    
    def create_directories(self):
        try:
            os.makedirs(f'{self.rootPath}\\{self.directory}\\{self.series}')
        except FileExistsError:
            pass
    
    def create_reference_list(self):
        self.reference_list = string.digits + string.ascii_lowercase
        self.hex_ref_list = self.reference_list[0:16]
        
    def create_gallery_list_to_search(self):
        self.gallery_search_list = []
        for i in self.reference_list:
            for j in self.reference_list:
                self.gallery_search_list.append(self.directory + self.series + i + j)
                
    def search_galleries_with_threads(self):
        self.list_of_galleries_checked = [self.exe.submit(check_single_IMX_gallery,galleryID = galleryID, ) for galleryID in self.gallery_search_list]
    
    def search_galleries_one_by_one(self):
        for gallery in self.gallery_search_list:
            check_single_IMX_gallery(self.gallery_search_list, self.rootPath)
                  
    def start_auto_search(self):
        if self.auto_search:
            self.get_root_path()
            self.ask_for_inputs()
            # self.create_directories()
            self.create_gallery_list_to_search()
            self.search_galleries_with_threads()
            self.auto_search = False
            
    def change_inputs(self):
        self.ask_for_inputs()
        
    def start_search(self):
        self.auto_search = True
        self.start_auto_search()
    
        
        
class check_single_IMX_gallery:
    def __init__(self, 
                 galleryID = None, 
                 rootPath = None,
                 auto_search = True):
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
        # print(self.path, self.directory, self.series)
        # print(os.path.exists(self.path+'\\Previews'))
        if os.path.exists(self.path+'\\Previews'):
            self.path += '\\Previews'
            # print(os.path.exists(self.path+f'\\{self.directory}'))
            if os.path.exists(self.path+f'\\{self.directory}'):
                self.path += f'\\{self.directory}'
                # print(os.path.exists(self.path+f'\\{self.series}'))
                if os.path.exists(self.path+f'\\{self.series}'):
                    self.path += f'\\{self.series}'
                else:
                    # print(self.path)
                    os.mkdir(self.path+f'\\{self.series}')
                    self.path += f'\\{self.series}'
            else:
                os.mkdir(self.path + f'\\{self.directory}')
                self.create_path()
        else:
            os.mkdir(self.path+'\\Previews')
            self.create_path()
            
    def save_preview_image(self):
        self.url = self.list_of_images[0] if self.number_of_images != None else None
        if self.url != None:
            self.load_gallery_page()
            self.check_response_code()
            # print(self.response.status_code)
            if self.good_response:
                # print('saving picture')
                try:
                    with open(f'{self.path}\\{self.galleryID}.jpg', 'wb') as image:
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
        if self.number_of_images > 25:
            return True
