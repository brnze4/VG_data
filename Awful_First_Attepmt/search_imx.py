
import os
import concurrent.futures
import string
import requests
from bs4 import BeautifulSoup

refList = []
listOfGalleries = []

def search_imx():
    
    global listOfGalleries
    
    listOfGalleries = []
    searchList = []
    directory = input('Enter directory number:')
    series = input('Enter gallery ID series (ex: x, y, or z):')
    workingDir = 'z:\\pictures\\previews\\'+series+'\\'
    if not os.path.exists(workingDir):
        os.mkdir((workingDir))
    create_reference_list()
    for char in refList:
        indx = char
        for char in refList:
            searchList.append(directory+series+indx + char)
    indx = 0            
    for galleryID in searchList:
        print(f'GalleryID: {galleryID}')
        galID = get_page(galleryID)
        soup = galID[0]
        galleryID = galID[1]
        make_img_list(soup, workingDir)
        if(len(linklist) > 25):
            link = [linklist[0][0], galleryID, linklist[0][2]]
            with concurrent.futures.ThreadPoolExecutor(max_workers = 3) as executor:
                executor.submit(dl_img, link)
            listOfGalleries.append(linklist)
            indx = indx +1
            print(f'\t Added: {galleryID}')
    print(len(searchList))
    print('Found {indx} galleries')
    someList = None
    return someList


def create_reference_list():
    global refList
    
    for i in range(10):
        refList.append(str(i))
    for char in string.ascii_lowercase:
        refList.append(char)
    return

def get_page(galleryID):
    url = 'https://imx.to/g/' + galleryID
    r = requests.get(url)
    return (BeautifulSoup(r.text, 'html.parser'), url.split('/')[-1])

search_imx()
