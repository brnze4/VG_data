# VG_data
Collaboration for sorting information on VG website.


Known issues:
  retrieve_gallery
      only grabs thumbnails, as opposed to full sized images.  There's an issue with processing the lead_in_url containing the file date information
      There's probably some better way to collect this information than using selenium.
  crawl_imx
    for some reason, after intial testing, it decided it was going to save the header information, and not the actual image data, 
      ...99 bugs in the code on my screen, 99 bugs in the code, take one down, patch it around, 107 bugs in the code on my screen...
    
To Do List:
  create some kind of cohesive UI, preferably GUI
  add support for more image hosts.
  add support for handling VG threads.
  add facial recognition for automatic image sorting
  figure out how to add TQDM progress bars.
  
