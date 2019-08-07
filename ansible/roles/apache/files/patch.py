from bs4 import BeautifulSoup
import random
import requests
import urllib3
import re
import os
from EmailApache import Email
from Version import Version


# Website and proxy information
lin_download_page = "https://httpd.apache.org/download.cgi?Preferred=http%3A%2F%2Fmirrors.ocf.berkeley.edu%2Fapache%2F"
win_download_page = ""
proxy = {"https": "https://..."}
security_page = "https://httpd.apache.org/security/vulnerabilities_"
url_VS = "https://docs.microsoft.com/en-us/visualstudio/install/visual-studio-build-numbers-and-release-dates?view=vs-2019"
mirror = "http://mirrors.ocf.berkeley.edu/apache//httpd/httpd-"

# Used throughout methods and changed often
downloaded_file = ""
previous_version = 0  # Keeps track of previous version to
new_version = 0  # Used to compare the two versions
path_name = "downloaded/"



# Compares the versions, calls the appropriate function to generate the correct
# url, and downloads the correct file
def main():
    
    # Declares global variables locally
    global new_version
    global previous_version
    global mirror
    global win_download_page
    global lin_download_page
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Reads in file to receive previous version
    get_old_version()
    
    # Retrieves new version
    version()
    
    # Checks to see if the version has updated since last download
    if new_version != previous_version:
        
        # Visual Studio version number
        vs = ""  
        # Changes the mirror to reflect the correct file on the website
        mirror = mirror + str(new_version) + ".tar.gz"
        
        # Retrieves Visual Studio version number
        vs = find_version_visual_studio().split(".")
        vs = vs[0] # Only need number before first .
        
        # Downloads the linux files
        download("linux", lin_download_page)
        
        # Sets Windows version
        win = "64"
        win_download_page = "https://www.apachelounge.com/download/VS" + str(vs) + "/binaries/httpd-" + new_version + "-win" + win + "-VS" + str(vs) + ".zip"
        
        # Downloads the windows files
        download("windows", win_download_page)
        
        # Sets Windows version
        win = "32"
        win_download_page = "https://www.apachelounge.com/download/VS" + str(vs) + "/binaries/httpd-" + new_version + "-win" + win + "-VS" + str(vs) + ".zip"
        
        # Downloads the windows files
        download("windows", win_download_page)
        
        # Updates the old_version file to contain the new version information
        update_file_new_version()
        
        # Calls email class to generate security email
        email = Email(security_page + new_version[:3].replace(".", "") + ".html", new_version, proxy, True)
        email.get_security_info()
        
    else:
        # Calls email to update users of previous patch security
        email = Email(security_page + previous_version[:3].replace(".", "") + ".html", previous_version, proxy, False)
        email.get_security_info()


# Reads old_version file in order to check if new_version and old_version match
def get_old_version():
    
    # Declares global variable locally
    global previous_version
    
    # Handles file not found exception
    try:
        
        # Retrieves old_version file
        ov_file = open('/old_version.txt', 'r')
        previous_version = ov_file.readline().rstrip('\\n')
        ov_file.close()
        
    # Reports file not found error
    except IOError as e:
        print("File get old_version.txt")
        print(e)


# Writes the new version number to the old_version file. Allows us to keep
# track of version changes
def update_file_new_version():
    
    # Declares global variables locally
    global new_version
    global previous_version
    
    # Handles file not found exception
    try:
        
        # Retrieves old version files
        ov_file = open('/old_version.txt', 'w')
        # Writes new version to file
        ov_file.write(str(new_version))
        ov_file.close()
        
    # Reports file not found error
    except IOError as e:
        print("File update old_version.txt")
        print(e)


# Calls version class for new version information
def version():
    
    # Declare global variables locally
    global lin_download_page
    global mirror
    global new_version
    
    # Calls Verision class to retrieve version number
    new_version = Version(lin_download_page, mirror, proxy, "apache").get_version()


# Searches the apache website for all relevant files. Calls appropriate download
# procedure.
# @param arch, windows or linux
# @param download_url, url to retrieve files
def download(arch, download_url):
    
    # URL of Apache update downloads
    html_content = requests.get(download_url, verify=False, proxies=proxy)
    # Parses website for the html content
    hrefs = BeautifulSoup(html_content.content, "html.parser")
    
    # Checks for errors
    if hrefs != -1:
        if arch == "linux":
            linux(hrefs)
        else:
            windows(html_content, download_url) 


# Retrieves the current version of visual studio. This will be used to create
# the url of the windows download file.
# @return visual studio version number
def find_version_visual_studio():
    
    # Declare global variables locally
    global url_VS
    
    # Declare variable to store version number
    vs = None
    
    # Retrieves html content
    html_content = requests.get(url_VS, verify=False, proxies=proxy)
    # Converts html to human readable information
    hrefs = BeautifulSoup(html_content.content, "html.parser")
    
    # Checks for errors
    if hrefs != -1:
        # Relevant information is in first td tag
        vs = hrefs.find("td")
        # Checks for errors
        if vs is not None:
            # Remove html syntax
            vs = re.sub("<td>", "", str(vs))
            vs = re.sub("<\/td>", "", str(vs))
    return vs


# Goes through linux download process
# @param hrefs, has html content from first url
def linux(hrefs):
    
    # Global variable declaration
    global path_name
    global mirror
    global downloaded_file
    
    # Retrieves file from linux mirror
    link = hrefs.find(href=re.compile(mirror))
    
    # Checks for errors
    if link is not None:
        
        # Retrieves the link
        url = link.get('href')
        
        # Adjusts html to create file name
        file_name = str(link).split(">")
        file_name = file_name[1].split("<")
        file_name = file_name[0]
        
        # Retrieves actual file
        downloaded_file = requests.get(url, verify=False, proxies=proxy)
        
        # Handles file path no found exception
        try:
            
            # Checks to see if tar directory exists
            if os.path.exists(path_name + "tar/"):
                # Creates new file in the directory
                with open(path_name + "tar/" + file_name, 'wb') as new_file:
                    new_file.write(downloaded_file.content)
            else:
                # Creates tar directory in downloaded directory
                os.makedirs(path_name + "tar/")
                # Creates new file in the directory
                with open(path_name + "tar/" + file_name, 'wb') as new_file:
                    new_file.write(downloaded_file.content)
                    
        # Reports file path not found 
        except IOError as e:
            print("Linux File Download")
            print(e)


# Goes through windows download process
# @param html, has html content from first url
# @param download, the download url
def windows(html, download):
    
    # Global variable declaration
    global path_name
    
    # Formats the file name
    file_name = str(download).split("/")
    file_name = file_name[6]
    
    # Handles file path not found exception
    try:
        
       # Checks to see if zip directory exists
       if os.path.exists(path_name + "zip/"):
         # Creates new file in directory
         with open(path_name + "zip/" + file_name, 'wb') as new_file:
               new_file.write(html.content)
       else:
         # Creates zip directory in downloaded directory
         os.makedirs(path_name + "zip/")
         # Creates new file in directory
         with open(path_name + "zip/" + file_name, 'wb') as new_file:
               new_file.write(html.content)
               
    # Reports file path not found exception
    except IOError as e:
      print("Windows File Download")
      print(e)


main()

