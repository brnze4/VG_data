from bs4 import BeautifulSoup
import os, time, string, concurrent.futures, pickle, requests, tkinter
from random import randrange as random
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import IPython.display as disp

class ImxWebScrape:
    def __init__(self):
        self.exe = concurrent.futures.ThreadPoolExecutor(max_workers = 10)
        self.create_reference_list()
        
    def gallery_download(self, 
                         multiple = False, 
                         multList = None, 
                         workingDirectory = None, 
                         galleryID = None, 
                         exe = None):
        # t1 = time.perf_counter()
        download = False
        print(f'gallery download. galleryID = {galleryID} workingDirectory = {workingDirectory}')
        if multiple == False and galleryID == None:
            self.set_working_dir('Pick model number or enter new name: ')
            temp = os.getcwd().split('\\')
            galleryID = temp[-1]
            self.galleryID = galleryID
            download = True
        elif multiple == True:
            temp = True
            while temp or temp.lower() != '' or temp.lower() == 'y':
                self.gallery_download()
                temp = input ('Continue? [Y]/N')
        
        # if gallery_download is called from a function exterior to this module, it can be passed
        # arguments to bypass getting command line user input.  The exterior module should handle
        # gathering user input
        elif galleryID != None and workingDirectory != None:
            print(f'GD: calling set_working_dir({workingDirectory}, {galleryID}')
            
            self.set_working_dir(prompt = None, 
                            workingDirectory = workingDirectory, 
                            galleryID = galleryID)
            print(f'GD: {os.getcwd()}')
            download = True
        else:
            print("Something went wrong, try again.")
            
        if download: #only execute if we have set a valid workingDir and have a valid gallery
            print(f'Downloading {galleryID}, workingDir = {os.getcwd()}')
            with open(self.rootPath+'\\order.txt', 'a') as f:
                f.write(os.getcwd()+'\n')
            self.workingDirectory = os.getcwd()+'\\'
            soup, location = self.get_page(galleryID)
            # linklist = self.make_img_list(soup, workingDirectory)
            # self.exe.map(self.dl_img, linklist)
            self.exe.submit(self.download)
        return 
    
    def download(self):
        # self.workingDirectory = os.getcwd()+'\\'
        workingDirectory = self.workingDirectory
        galleryID = self.galleryID
        print(self.workingDirectory)
        soup, location = self.get_page(galleryID)
        linklist = self.make_img_list(soup, workingDirectory)
        print(linklist[0])
        self.exe.map(self.dl_img, linklist)
        return
        
    
    def check_files(self, linklist):
        retVal = False
        if len(os.listdir()) != len(linklist):
            # with concurrent.futures.ThreadPoolExecutor(max_workers = 9) as exe:
            self.exe.map(self.dl_img, linklist)
            retVal = True
        return retVal
    
    def deep_search(self, path, single):
        directory = input('Directory: ')
        start_index = int(input('Offset Start Index? '))
        if start_index == '':
            start_index = 0
        all_series = self.create_reference_list()
        for one_series in all_series[start_index::]:
            self.search_imx(path, single, directory, one_series)
        return
    
    def search_imx(self, path, single, directory = None, series = None):
        searchList = []
        os.chdir(path)
        
        #if we're only searching a single series, get the series and directory
        #if multiple series are getting searched, skip this because the values 
        #are getting passed in from deep_search()
        if single:
            directory = input('Enter directory number:')
            series = input('Enter gallery ID series (ex: x, y, or z):')
        
        #this is stuff to handle searching for directories that are less than
        #4 characters in length.  The _ is used for the windows file directory
        #and then later converted back to an empty string for the URL
        if directory ==  '':
            directory ='_'
        if series == '':
            series == '_'
            
        #attempt to goto the directory path
        try:
            os.chdir(f'{os.getcwd()}\\previews\\'+directory)
        #if the directory path doesn't exist, make it
        except FileNotFoundError:
            os.mkdir(f'{os.getcwd()}\\previews\\'+directory)
            os.chdir(f'{os.getcwd()}\\previews\\'+directory)
        #if the directory path exists, just goto it
        except FileExistsError:
            os.chdir(f'{os.getcwd()}\\previews\\'+directory)
            
        #set the path for the series folder
        workingDir = f'{os.getcwd()}\\' + series +'\\'
        
        #get into the series folder
        if not os.path.exists(workingDir):
            os.mkdir((workingDir))
            os.chdir(workingDir)
    
        if directory == '_':
            directory = ''
        if series == '_':
            series == ''
        searchList = self.make_list_of_galleries(directory, series, workingDir)
        
        # use concurrent.futures to create a pool of check_gallery threads, this is 
        # due to limitations in python based on the GIL and I/O activities
        # max_workers 20 may be a bit high
        # with concurrent.futures.ThreadPoolExecutor(max_workers = 9) as exe:
        results = [self.exe.submit(self.check_gallery, galleryID) for galleryID in searchList] #galleryID is a list
        return results
    
    def make_list_of_galleries(self, directory, series, workingDir):
        searchList = []
        for char in self.refList:
            indx = char
            for char in self.refList:
                searchList.append((directory+series+indx + char, workingDir))
        return searchList
    
    def crawl_single(self, url, hex_only = False):
        #take an full size image link, remove the file.jpg from the end
        hold = url.split('/')[-1].split('.')[0]
        parent = 'Crawl'
        
        try:
            os.chdir(os.getcwd()+f'\\{parent}')
        except FileNotFoundError:
            os.mkdir(os.getcwd()+f'\\{parent}')
            os.chdir(os.getcwd()+f'\\{parent}')
                
        try:
            os.chdir(os.getcwd()+f'\\{hold}')
        except FileNotFoundError:
            os.mkdir(os.getcwd()+f'\\{hold}')
            os.chdir(os.getcwd()+f'\\{hold}')
            
        url = url.replace(url.split('/')[-1], '') 
        length = len(hold)
        ref = self.create_reference_list()
        doubleRef = []
        
        if hex_only:
            ref = ref[:16]
            
            for i in ref:
                for j in ref:
                    for k in ref:
                        doubleRef.append(hold[0:length-3]+i+j+'.jpg')
        else:
            for i in ref:
                for j in ref:
                    doubleRef.append(hold[0:length-2]+i+j+'.jpg')
                    
        links = []
        for i in doubleRef:
            links.append(url+i)
            
        self.dl_img(links, 1)
        # with open('links.txt', 'w') as f:
        #     for result in results:
        #         f.write(result.result())
        return links
    
    
    
    #galleryID is a tuple (galleryID, workingDir)
    def check_gallery(self, galleryID, download_preview = True):
        retList = None
        # print(f'C_g {galleryID}')
        # get page will gather the data from the URL imx.to/g/{galleryID} and return
        # a tuple of the form (BS4 Soup Object, galleryID)
        try:
            soup = self.get_page(galleryID[0])[0]
        except TypeError:
            print(f"something went wrong with {galleryID}")
        
        # linkList is a list of links to download.  Each link is stored in the format
        # [URL, fileName, directory to place the image]
        # make_img_list needs the soup variable, and the path is optional.
        # we choose to use this option so the program can move on while lumping data
        # into the threadpool, without screwing up storage locations
        linkList = self.search_imx_linklist(soup)
        #print(threading.active_count())
        
        print(f'C_g {galleryID[0]}\t length LL = {len(linklist)}\tlink[0] = {linkList[0]}')
        if(len(linkList) > 30):
            with open(f'{linkList[0][2]}{galleryID[0]}.txt', 'w') as fb: #save built link list
                for link in linkList:    
                    fb.write(f'{link[1]}  {link[0]}\n')
            link = [linkList[0], galleryID[0], galleryID[1]] #dl preview, grab the first link from linkList
            # and store the file as galleryID.jpg in the location *.*\Previews\Directory Number\Series Number\
            # submit the link to the ThreadPool, this way we don't have to wait for the I/O return to continue
            # processing galleries:
            print(f'link = {link}')
            if download_preview:
                # with concurrent.futures.ThreadPoolExecutor(max_workers = 1) as executor:
                self.exe.submit(self.dl_img, link)
                print(f'\t Added: {galleryID}')
            retList = galleryID[0]
        return retList
    
    def search_imx_linklist(self, soup):
        all_images = soup.find_all('img')
        all_images = [image.get('src') for image in all_images if image.get('class').find('imgtooltip') != -1 and image.get('src').find('imx.to') != -1]
        return all_images
    
    def print_list(self, someList, prompt = None):
        if prompt is not None:
            print(prompt)
        if someList != None:
            for i, j in enumerate(someList):
                print(f'{i}: {j}')
        return
    
    
    # get_page takes a galleryID, utilizing the requests module, gathers the info
    # from the web, and creates a soup object.  Rudimentary checks are performed,
    # specifically, if the page is 404.  Futher checks may later get added.  Most 
    # errors are 503, server busy, so just wait some random amount of seconds and try
    # again.  This function is recursive with regards to trying again, until it works.
    # it's some pretty lazy recursion
    def get_page(self, galleryID):
        url = 'https://imx.to/g/' + galleryID
        retVal = None
        try: 
            r = requests.get(url)
            # print(f' Gallery {galleryID} status code {r.status_code}')
            retVal = True
        except requests.exceptions.HTTPError:
            if r.status_code != 404:
                time.sleep(random(0,7))
                print(' Gallery {galleryID} status code {r.status_code}')
                self.get_page(url)
            else:
                print(f'Error: {r.status_code} on {url} from get_page method') 
        except:
            pass
        if retVal:
            retVal = (BeautifulSoup(r.text, 'html.parser'), url.split('/')[-1])
        return retVal
    
    def make_img_list(self, soup, workingDir=f'e:\\pictures\\'):
        linklist = []
    #    print(type(soup))
        i = 1
        url_starter = self.get_url_starter(self.get_an_image_preview_link(soup)).split('/i/')[0]
        # url_starter.pop(-1)
        # url_starter = '/'.join(url_starter)
        #ask BS4 to find all the img references in the soup object
        for _, link in enumerate(soup.find_all('img')):
            # there are two links to each image, imgtooltip was a arbitrary choice of the two
            # identical links, some of the links are based on //domain.com/restOfLink, we don't want those
            # because they're garbage pictures to make the site look pretty
            if not link.get('src').find('http') and link.get('class')[0] == 'imgtooltip':
                image_file = link.get('src').split('/t/')[-1]
                fixed = url_starter + '/i/' + image_file
                linklist.append([fixed, i, workingDir])
                i += 1
        return linklist
    
    def get_an_image_preview_link(self, soup):
        temp = soup.find_all('a')
        length = len(temp)
        print(temp[length//2].get('href'))
        return temp[length//2].get('href')
    
    # download image takes a list into the variable img_url.  This list should consist of
    # [URL, filename, directory to save the file]  The function has some rudimentary error
    # checking for bad HTTP response codes, it looks for 400 series error codes, which 
    # should indicate a major problem with the URL, if the site responds with anything that's 
    # not 200, or a 400 series, it just tries again after a delay.
    def dl_img(self, img_url, new_method = 0, attempt = 0): #img_url passed as list
        retVal = None
        if new_method == 0:  #this is the original single search method, a interable method
                             # is implemented in the else statement
            try:                 
                r = requests.get(img_url[0])
                # print(r.status_code)
            except ConnectionError:
                print(f'ConnectionError: {img_url[0]}')
            try:
                r.raise_for_status()
                #         path/imgID#.jpg
                with open(img_url[2]+str(img_url[1])+'.jpg', 'wb') as f:
                    f.write(r.content)
                    # print(img_url)
                retVal = img_url[0] # return the URL, this can be useful for creating a 
                                    # list of all the URL's retrieved for error checking
            
            #check for 403 and 404 errors. Skip link if 404, try other links if 403
            except requests.exceptions.HTTPError:
                if r.status_code < 400 or r.status_code > 499:
                    time.sleep(random(0,7))
                    self.dl_img(img_url)
                else: #we found a 400 series error code, don't loop, just return
                    print(f'Error: {r.status_code} on {img_url[0]}')
            except:
                pass
        # You can pass in a list of URLS to img_url, and flag it with new_method = 1, this will unpack the list 
        # and create a threadpool of images to download, it just sends each list from the parent list to dl_img as
        # single input for the old method above, this method will return a list of URLS instead of a single URL string
        # using this is only good if you know that os.getcwd() won't change before the threadpool completes execution
        else: ##working directory is fixed, needs to be coded flex later
            # with concurrent.futures.ThreadPoolExecutor(max_workers=9) as exe:
            # print('dlimg multi')
            folder = img_url[0].split('/')[-1].split('.')[0]
            retVal =  [self.exe.submit(self.dl_img, [link, i, os.getcwd()+'\\Random\\'+folder]) for i, link in enumerate(img_url)]
           
        return retVal
    
    
    
    
    def set_working_dir(self,
                        prompt, 
                        multiple = None, 
                        saveFile = '\\folderList.txt', 
                        workingDirectory = None, 
                        galleryID = None):
        #set path to save file
        # print(f'SWD: workingDirectory={workingDirectory}, galleryID = {galleryID}')
        savePath = os.getcwd() + saveFile
        
        temp = [item for item in os.listdir() if os.path.isdir(item)]
        temp.sort()
        # for item in os.listdir():
        #     if os.path.isdir(f'{os.getcwd()}\\{item}'):
        #         temp.append(item)
        
        # print(f'SWD: check gallerID == {galleryID}, workingDirectory: {workingDirectory}')
        if galleryID == None:
            self.print_list(temp, prompt)
            workingDirectory = input()
            # print(type(temp), type(folder))
            galleryID = self.get_gallery_ID(savePath, temp)
        else:
            workingDirectory = ''
        # print(f'SWD: Dump Temp as pickle')
        with open(os.getcwd()+saveFile, 'wb') as fp:
            fp.truncate(0)
            pickle.dump(temp,fp)
        # print('cleared file dump')
            
        try:
            # print(f'SWD: try 1')
            os.chdir(os.getcwd()+f'\\{temp[int(workingDirectory)]}')
        except ValueError:
            # print(f'SWD: ValueError 1')
            try:
                os.mkdir(os.getcwd()+f'\\{workingDirectory}')
                os.chdir(os.getcwd()+f'\\{workingDirectory}')
            except FileExistsError:
                os.chdir(os.getcwd()+f'\\{workingDirectory}')
        except FileNotFoundError:
            # print(f'SWD: FNEF 1')
            os.mkdir(os.getcwd()+f'\\{workingDirectory}')
            os.chdir(os.getcwd()+f'\\{workingDirectory}')
    
        try: 
            print("try2")
            os.chdir(os.getcwd()+f'\\{galleryID}')
        except:
            print('general except')
            os.mkdir(os.getcwd()+f'\\{galleryID}')
            os.chdir(os.getcwd()+f'\\{galleryID}')
        print(f'SWD: {os.getcwd()}')
        return  
    
    def get_gallery_ID(self, save = None, saveFile = 'dump.txt'):
        galleryID = self.get_valid_input("Gallery ID:")
        if galleryID == '':
            self.check_quit(galleryID, saveFile, save)
        
        return galleryID
    
    def check_quit(self, 
                   operation = None, 
                   save = None, 
                   saveFile = 'dump.txt'):
        if(operation == ''):
            temp = input('No value entered, quit? [Y]/N: ').lower()
            if temp == '' or temp == 'y':
                raise SystemExit
            else:
                if type(operation) == type(lambda x:x): retVal = operation()
                else: retVal = operation
        else: retVal = operation
        return retVal 
    
    
    def fix_imx(self, link):
        if link.find('small') > 0:
            temp = link.replace('imx.to/upload/small', 'i001.imx.to/i')
        elif link.find('u/t'):
            temp = link.replace('u/t', 'i')
            temp = temp.replace('imx', 'i.imx')
        return temp
    
    def get_directory(self):
        root = tkinter.Tk()
        root.withdraw()
        self.rootPath = filedialog.askdirectory()
        print(self.rootPath)
    
    def get_file_name(self):
        root = tkinter.Tk()
        root.withdraw()
        return filedialog.askopenfilename()
    
    def create_reference_list(self):
        self.refList = []
        
        for i in range(10):
            self.refList.append(str(i))
        for char in string.ascii_lowercase:
            self.refList.append(char)
        
    
    def get_valid_input(self, prompt = 'Enter Input: ', save = None, saveFile = 'dump.txt'):
        x = input(prompt)
        return self.check_quit(x, saveFile, save)
    
    def browse_gallery(self):
        galleryList = [item.split(' ')[-1] for item in open(self.get_file_name()).read().split('\n')]
        for URL in galleryList:   
            print(URL)
            disp.Image(requests.get(URL).content, width = 250)
            if input("Continue? [y]/n").lower() == 'n':
                break
        return
    
    
    #fails to set imgbox links correctly, come back and fix?
    def scrape_image_hosting_site(self, URL):
        b = [a.get('src') for a in BeautifulSoup(requests.get(URL).text, 'html.parser').find_all('img')]
        c = [item for item in b if  item.find('imx') != -1 or 
                                    item.find('pixhost') != -1 or 
                                    item.find('imgbox') != -1 or
                                    item.find('acid') != -1]
       
        for i, _ in enumerate(c):
            if c[i].find('imx') != -1:
                c[i] = self.fix_imx(c[i])
            elif c[i].find('pixhost') != -1:
                c[i] = c[i].replace('pixhost.to/show', 'img43.pixhost.to/images').replace('thumbs', 'images').replace('//t', '//img')
            elif c[i].find('imgbox') != -1:
                c[i] = c[i].replace('thumbs', 'images').replace('_b', '_o')
            elif c[i].find('acid') != -1:
                c[i] = c[i].replace('small', 'big')
        workingDir = f'{path}\\random\\' + c[0].split('/')[-1].split('.')[0] + '\\'
    
        if not os.path.exists(workingDir):
            os.mkdir(workingDir)
        # print(c)
        [self.exe.submit(self.dl_img, [link, i, workingDir]) for i, link in enumerate(c)]
        return
    
    def get_url_starter(self, url):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument()
        driver = webdriver.Chrome(options = chrome_options,
                                  executable_path=self.rootPath+'\\chromedriver.exe')
        # driver = webdriver.Chrome()
        # driver.implicitly_wait(10)
        driver.get(url)
        driver.find_element_by_tag_name('body').click()
        try:
            driver.find_element_by_id('continuebutton').click()
        except:
            driver.find_element_by_id('continuetoimage').click()
        driver.find_element_by_tag_name('body').click()
        driver.find_element_by_class_name('centred').click()
        # time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[1])
        temp = driver.current_url
        driver.quit()
        return temp

'''########################################################################'''
if __name__ == '__main__':
    scraper = ImxWebScrape()
    linklist = []
    listOfGalleries = []
    results = []
    indx = 0
    options =['Download from IMX Gallery', 
              'Search IMX for Galleries', 
              'Download all images from URL', 
              'Crawl from single link', 
              'Choose a Gallery To Browse', 
              'Exit']
    site_list = ['imx', 'pixhost', 'imgbox']
    
    scraper.get_directory()
    path = scraper.rootPath
    savePath = path
    
    while True:
        
        
        os.chdir(path)
        scraper.print_list(options, 'Pick an option:')
        branch = input()
        mult = None
        if branch == '0':
            os.chdir(path)
            # mult = input("Multiple? Y/[N]:")
            if mult == 'y' or mult == 'Y':
                # get_files(mult)
                print('Whoops, guess that didn\'t work, try again')
                # soup = gallery_download(multiple = True)
            else:
                soup = scraper.gallery_download()
                
        elif branch == '1':
            os.chdir(path)
            single = input('Multi? Y/[N]')
            single = True if single.lower() == 'n' or single.lower() == ''  else False
            print(single)
            if single:
                listOfGalleries = scraper.search_imx(path, single)            
            else:
                scraper.deep_search(path, single)
        elif branch == '2':
            os.chdir(f'{path}')
            url = input('URL: ')
            if url != '':
                scraper.scrape_image_hosting_site(url)         
        elif branch == '3':
            url = input('URL: ')
            links = scraper.crawl_single(url, hex_only = bool(input("hex? True/[False]")))
            os.chdir( path)
            print('Crawl Complete')
        elif branch == '4':
            scraper.browse_gallery()
        
        elif branch == '5':
            scraper.exe.shutdown()
            break
        
