import time
import requests
from bs4 import BeautifulSoup
from random import randrange as random

#This class is designed to be the container holding a soup object, a response object
#it has the ability to save images if needed, based on the url passed in.   
class Imx_download:
    def __init__(self, url, path):
        self.url = url
        self.path = path
    
    def do_it(self):
        """
        Automated script to access a given URL and save the image data from
        the URL.  Only works if URL points directly to an image.

        Returns
        -------
        None.

        """
        self.index = self.url.split('/')[-1]
        self.file_path = '\\'.join([self.path, self.index])
        self.page = open_webpage(self.url)
        self.save_content()
        
    def save_content(self):
        """
        Saves the .content from a requests object to self.file_path as bytes

        Returns
        -------
        retVal : String
            If the site has a good HTTP response, and an image is saved, returns
            'Saved' else returns 'Bad Image'

        """
        retVal = 'Bad Image'
        if self.page.good_response:
            # if len(self.page.response.content) > 8000: 
            with open(self.file_path, 'wb') as fb:
                      fb.write(self.page.response.content)
            retVal == 'Saved'
        return retVal

class open_webpage:
    def __init__(self, url):
        self.url = url
            
    def load_gallery_page(self):
        """
        Creates a request object from self.url
        
        Returns
        -------
        None.

        """
        self.response = requests.get(self.url)
        
    def make_soup_object(self):
        """
        Create a soup object from the request object obtained in load_gallery_page()

        Returns
        -------
        None.

        """
        self.soup = BeautifulSoup(self.response.text, 'html.parser') if self.good_response else None
    
        
    
    def check_response_code(self):
        """
        Check the HTTP response code for self.URL
        If a bad response code is receieved (503, 400-499), the method will 
        call time.sleep() for a random float interval between 0.000 and 7.000
        seconds.  This is to help prevent overloading a server with bad requests

        Returns
        -------
        self.good_resonse : Bool 
            self.good_response indicates if an HTTP response other than a 400 series response
            was issued by the the server
        """
        self.good_response = False
        sleep = 70/random(10,100)
        if self.response.status_code == 503:
            time.sleep(sleep)
            print(f'Server Error {self.response.status_code}: Attempting to load gallery {self.url} again in {sleep} seconds.')
            self.make_soup()
        elif self.response.status_code == 404:
            print(f'Error: 404.  URL: {self.url}  Pausing {sleep} seconds before next call.')
            time.sleep(sleep)
        elif self.response.status_code >= 400 and self.response.status_code < 500:
            if self.soup == None:
                print(f'Error: IMX gallery {self.url} responsed {self.response.status_code}, gallery not retreived.')
            elif self.preview_url != None:
                print(f'Error: Unable to retrieve gallery {self.url} preview image.  Server responded {self.response.status_code}')
            time.sleep(sleep)
        else:
            self.good_response = True
        return self.good_response
    
    def make_soup(self):
        """
        call requests.get(self.url)
        if good response:
            make a soup object from the response.text

        Returns
        -------
        None.

        """
        self.load_gallery_page()
        if self.check_response_code():
            self.make_soup_object()


    def get_content(self):
        """
        Attempt to access the URL
        if good response
            self.image is set to the response.content

        Returns
        -------
        None.

        """
        self.load_gallery_page()
        if self.check_response_code():
            self.image = self.response.content


# Testing code
# if __name__ == '__main__':
#     url = input('URL: ')
#     exe = ThreadPoolExecutor(max_workers=15)
#     rootPath = 'z:\\Pictures'
#     dl = imx_crawl(url, rootPath, exe)
#     exe.shutdown()
