import os
import tkinter
from tkinter import filedialog

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
        root.destroy()
    
    def create_path(self):
        if not os.path.exists(f'{self.save_path}\\{self.galleryID}'):
            try:
                os.makedirs(f'{self.save_path}\\{self.galleryID}')
                self.save_path = f'{self.save_path}\\{self.galleryID}'
            except:
                print(f'Failed to make path {self.save_path}\\{self.galleryID}\nExiting')
                raise SystemExit
                
    def do_it(self):
        self.get_parent_folder()
        self.create_path()
        
