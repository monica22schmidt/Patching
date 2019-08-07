from bs4 import BeautifulSoup
from Email import EmailGenerator
from Version import Version
import requests
import re
import time
import os
import urllib3

url_beginning = "https://d3pxv6yz143wms.cloudfront.net/"  # nonvariable part of corretto url
previous_version = 0  # keeps track of previous version to check if it has changed
new_version = 0  # used to compare the two versions
corretto_version = 8  # specifies if it is 11 or 8
time_checked = 0 # Current date and time information of program run


# Reads and writes time and version information to and from a file. Compares 
# the new version, with the old. Calls download function to write files to 
# computer. Runs main twice for corretto 8 and 11.
def main():
    
    # Declares global variables locally
    global new_version
    global previous_version
    global corretto_version
    global time_checked

    # Keeps track of the number of times executed
    i = 0
    
    # Disables warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Runs process twice for 8 and 11
    while i < 2:
        
        # Reads in old version
        get_old_version_and_time()
        
        # Retrieves new version
        version()
        
        # Checks to see if the version has updated since last download
        if new_version != previous_version:
            
            # Writes necessary files to computer
            download()
            
            # Calls EmailGenerator class to create the security email
            # https://alas.aws.amazon.com/alas2.html - security information is located here
            EmailGenerator("https://alas.aws.amazon.com/alas2.html", new_version, True,
                           {"https": "https://..."}, time_checked).get_security_info()
                           
            # Changes time checked to the current date and time
            time_checked = time.localtime(time.time())
            
        else:
            
            # Calls EmailGenerator class to create the security email
            EmailGenerator("https://alas.aws.amazon.com/alas2.html", new_version, False,
                           {"https": "https://..."}, time_checked).get_security_info()
                           
        # Updates time_checked to current time
        # Updates the old_version file to contain the new version information
        update_file_new_version_and_time()
        
        # Increases execution number
        i += 1
        
        # Changes corretto version specifier to 11
        corretto_version = 11


# Reads old_version file in order to check if new_version and old_version
# match. Also retrieves old time stamp.
def get_old_version_and_time():
    
    # Declares global variables locally
    global corretto_version
    global previous_version
    global 
    
    # Handles file not found exception
    try:
        
        # Opens old version file
        ov_file = open('/old_version' + str(corretto_version) + '.txt',
                       'r')
        previous_version = ov_file.readline().rstrip('\n')
        
        # Reads in time string
        time_tuple = (ov_file.readline())
    
        # Converts time string into time tuple 
        time_checked = time.struct_time(int(x) for x in time_tuple.split(","))
        
        ov_file.close
        
    except IOError:
        print("File old_version" + str(corretto_version) + ".txt not in directory while getting version")


# Writes the new version number to the old_version file. Allows us to keep
# track of version changes.
def update_file_new_version_and_time():
    
    # Declares global variables locally
    global corretto_version
    global new_version
    global time_checked
    
     # Handles file not found exception
    try:
        
        # Opens old version file to write to it
        ov_file = open('/old_version' + str(corretto_version) + '.txt',
                       'w')
        
        # Writes new version to file
        ov_file.write(new_version + "\n")
        
        # Turns tuple of ints into string
        ov_file.write(str(time_checked.tm_year) + ", " + str(time_checked.tm_mon) + ", " + str(time_checked.tm_mday)
                      + ", " + str(time_checked.tm_hour) + ", " + str(time_checked.tm_min) + ", " +
                      str(time_checked.tm_sec) + ", " + str(time_checked.tm_wday) + ", " + str(time_checked.tm_yday)
                      + ", " + str(time_checked.tm_isdst))
                      
        ov_file.close()
        
    except IOError:
        print("File old_version" + str(corretto_version) + ".txt not in directory while getting new version file")


# Calls Version class to retrieve version information
def version():
    
    # Declare global variables locally
    global corretto_version
    global new_version
    global url_beginning
    
    # URL of corretto update downloads
    url = "https://docs.aws.amazon.com/corretto/latest/corretto-" + str(corretto_version) + "-ug/downloads-list.html"
    
    # Calls version class
    new_version = Version(url, url_beginning, {"https": "https://..."},
                          "corretto").get_version()


# Searches the amazon corretto website for all relevant files. Parses for file 
# names to use as specifiers. Then downloads file onto the host computer.
def download():
    
    # Declares global variables locally
    global corretto_version
    
    # URL of corretto update downloads
    html_content = requests.get("https://docs.aws.amazon.com/corretto"
                                "/latest/corretto-" + str(corretto_version) + "-ug/downloads-list.html")
    
    # Parses website for the html content
    urls = BeautifulSoup(html_content.content, "html.parser")
    
    # Checks for errors
    if urls != -1:
    
        # Retrieves the first URL with version information
        links = urls.findAll(href=re.compile(url_beginning + new_version))
    
        # Runs through all links from download page
        for link in links:
    
            # Checks for errors
            if link != -1:
                
                # Retrieves url from html
                url = link['href']
                
                # Checks for errors
                if url != -1:
                    
                    # Rules out irrelevant files on the website
                    if "deb" not in str(url) and "msi" not in str(url) and "jre" not in str(url) and "sig" not in str(
                            url) and "aarch64" not in str(url) and "amzn2" not in str(url) and (("windows" in str(url)
                                    or "linux" in str(url)) or "rpm" in str(url)):
                    
                        # Retrieves and formats file name
                        retrieving_name = str(link).split(">")
                        file_name = retrieving_name[1]
                        file_name = file_name[:-3]
                    
                        # Retrieves file to be downloaded
                        downloaded_file = requests.get(url)
                        
                        # Specifies corretto_version for path
                        cv = str(corretto_version)
                        
                        # Handles file not found exceptions
                        try:
                            
                            # Designated path to downloaded directory
                            path_name = "/downloaded/"
                            
                            # Checks to see if the extracted link is a linux file
                            if "linux" in file_name or "rpm" in file_name:
                                # Checks to see if the linux directory is in downloaded
                                if os.path.exists(path_name + cv + "/linux/"):
                                    # Creates the tar and rpm files
                                    with open(path_name + cv + "/linux/" + file_name, 'wb') as new_file:
                                        new_file.write(downloaded_file.content)
                                        
                                else:
                                    # Creates linux directory is in downloaded directory
                                    os.makedirs(path_name + cv + "/linux/")
                                    # Creates the linux tar and rpm files
                                    with open(path_name + cv + "/linux/" + file_name, 'wb') as new_file:
                                        new_file.write(downloaded_file.content)
                                        
                            else:
                                
                                # Checks to see if the windows directory exists
                                if os.path.exists(path_name + cv + "/windows/"):
                                    # Creates the windows zip file
                                    with open(path_name + cv + "/windows/" + file_name, 'wb') as new_file:
                                        new_file.write(downloaded_file.content)
                                
                                else:
                                    # Creates windows directory in downloaded directory
                                    os.makedirs(path_name + cv + "/windows/")
                                    # Creates the windows zip file
                                    with open(path_name + cv + "/windows/" + file_name, 'wb') as new_file:
                                        new_file.write(downloaded_file.content)
                
                        # Catches file not found error
                        except IOError as e:
                            print("can't write files download ")
                            print(e)


main()
