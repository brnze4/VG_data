
from imx2 import *
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import messagebox, filedialog, Text
import os, requests, string
from bs4 import BeautifulSoup as bs
import pyperclip, requests, pickle, imx2
import concurrent.futures
# from download_popup import *

# HEIGHT = 480
# WIDTH = 800

HEIGHT = 960
WIDTH = 1600
IMG_VIEW_RELY = .9
IMG_VIEW_RELX = 1
UNITY = 1

def get_scale_factor(image):
    x, y = image.size
    scale_x = scale_y = HEIGHT*IMG_VIEW_RELY/y
    
    return (scale_x, scale_y)

def get_scaled_dimensions(image):
    
    x, y = image.size
    scale_x = scale_y = HEIGHT*IMG_VIEW_RELY/y
    if x*scale_x > WIDTH:
        scale_x = scale_y = WIDTH/IMG_VIEW_RELY/x
    #     win.geometry(f'{int(x*scale_x)}x{HEIGHT}')
    # else:
    #     win.geometry(f'{WIDTH}x{HEIGHT}')
    # print(x, y, scale_x, scale_y)
    return (int(scale_x*x), int(scale_y*y))    

def copy_url():
    pyperclip.copy('https://imx.to/g/'+galleryData.get())
    print('https://imx.to/g/'+galleryData.get())

def next_img():
    try:
        img = next(images)  # get the next image from the iterator
        # print(img)
        galleryData.set(img.split('\\')[-1].split('.')[0])
        # print(galleryData.get().upper())
        win.title(f'Gallery {galleryData.get().upper()} Preview')
        # if img.split('.')[-1] != 'jpg':
        #     img = next(images)
        # btn_copy['text'] = img.split('\\')[-1].split('.')[0]
    except StopIteration:
        return  # if there are no more images, do nothing
    except OSError:
        next_img()

    # load the image and display it
    img = Image.open(img)  #open a .jpg
    scale = get_scaled_dimensions(img) #find scale factor based on resolution
    
    #take .jpg, resize it based on scale, create tk friendly .bmp, assign to win
    img = ImageTk.PhotoImage(img.resize(scale, resample = Image.HAMMING), master = win) #take the bmp, resize it, and display create a new object
    panel.img = img  # keep a reference so it's not garbage collected
    panel['image'] = img  #update the image displayed.
    return scale

def choose_folder():
    temp_win = tk.Tk()
    
def download_gallery(executor):
    workingDirectory = filedialog.askdirectory().replace('/', '\\')
    os.chdir(workingDirectory)
    galleryID = galleryData.get()
    print(f'GUI: GalleryID {galleryID}')
    gallery_download(multiple = False, multList = None, 
                     workingDirectory = workingDirectory, 
                     galleryID = galleryID,
                     exe = executor)

def stop(executor):
    messagebox.showinfo(message="Shutting down threads before exiting.\nProgram will exit upon completion")
    executor.shutdown(wait = True)
    win.destroy()
    raise SystemExit
    
if __name__ == '__main__':
    executor = concurrent.futures.ThreadPoolExecutor(max_workers = 10)
    win = tk.Tk()
    win.title("Gallery Preview")
    win.iconbitmap()
    win.geometry(f'{str(WIDTH)}x{str(HEIGHT)}')
    win.resizable(True, True)  # fix window
    
    galleryData = tk.StringVar()
    
    img_frame = tk.Frame(win, bg = '#878787')
    img_frame.place(relx = 0, rely =0, relwidth = 1, relheight = IMG_VIEW_RELY)
    
    bottom_frame = tk.Frame(win, bg = '#063b3b')
    bottom_frame.place(relx = 0, rely = IMG_VIEW_RELY, relwidth = 1, relheight = 1-IMG_VIEW_RELY)
    
    
    panel = tk.Label(master = img_frame, bg = '#878787')
    panel.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
    
    btn = tk.Button(master = bottom_frame, text='Next Image')
    btn.place(relx = 1/3, rely = 0, relheight = .5, relwidth = 1/3)
    
    btn_copy = tk.Button(master = bottom_frame, text = 'Copy URL', command = copy_url)
    btn_copy.place(relx = 2/3, rely = 0, relheight = .5, relwidth = 1/3)
    
    btn_download = tk.Button(master = bottom_frame, text = "Download Gallery", command = lambda: download_gallery(executor))
    btn_download.place(relx = 0, rely = 0, relheight = .5, relwidth = 1/3)
    
    btn_exit = tk.Button(master = bottom_frame, text = 'Exit', command = lambda: stop(executor))
    btn_exit.place(relx = 0, rely = .5, relwidth = 1, relheight = .5)
    
    os.chdir(filedialog.askdirectory())
    images = [os.path.realpath(filename) for filename in os.listdir() if filename.find('jpg') > 0]
    images = iter(images)  # make an iterator
        
    btn['command'] = next_img
    
    # show the first image
    next_img()
    # print(panel['image'])
    win.mainloop()


# response = BeautifulSoup(requests.get(f'https://imx.to/g/{a[0]}').text, 'html.parser').find_all('img')
# links = [link.get('src') for link in response if link.get('src').find('jpg') >0]
