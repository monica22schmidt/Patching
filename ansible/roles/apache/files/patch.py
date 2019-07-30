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
proxy = {"https": "https://...."}
security_page = "https://httpd.apache.org/security/vulnerabilities_"
# Used throughout methods and changed often
downloaded_file = ""
mirror = "http://mirrors.ocf.berkeley.edu/apache//httpd/httpd-"
previous_version = 0  # keeps track of previous version to
new_version = 0  # used to compare the two versions
path_name = "/downloaded/"
url_VS = "https://docs.microsoft.com/en-us/visualstudio/install/visual-studio-build-numbers-and-release-dates?view=vs-2019"


# Compares the versions, calls the appropriate function to generate the correct
# url and download the correct file
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
        vs = ""
        # Changes the mirror to reflect the correct file on the website
        mirror = mirror + str(new_version) + ".tar.gz"
        # Downloads the linux files
        download("linux", lin_download_page)
        win = "64"
        vs = find_version_visual_studio()
        vs = vs[:2]
        win_download_page = "https://www.apachelounge.com/download/VS" + str(
            vs) + "/binaries/httpd-" + new_version + "-win" + win + "-VS" + str(vs) + ".zip"
        # Downloads the windows files
        download("windows", win_download_page)
        win = "32"
        win_download_page = "https://www.apachelounge.com/download/VS" + str(
            vs) + "/binaries/httpd-" + new_version + "-win" + win + "-VS" + str(vs) + ".zip"
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
        ov_file = open('/etc/ansible/roles/apache/files/old_version.txt', 'r')
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
        ov_file = open('/etc/ansible/roles/apache/files/old_version.txt', 'w')
        # Writes new version to file
        ov_file.write(str(new_version))
        ov_file.close()
    # Reports file not found error
    except IOError as e:
        print("File update old_version.txt")
        print(e)


# Opens base website and retrieves the first url with the version number,
# splits that link in order to retrieve the version number, and stores
# the version in the global variable new_version.
def version():
    # Declare global variables locally
    global lin_download_page
    global mirror
    global new_version
    # Calls Verision class to retrieve version number
    new_version = Version(lin_download_page, mirror, proxy, "apache").get_version()


# Searches the apache website for all relevant files. Parses for file names
# to use as specifiers. Downloads files onto the host computer.
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


# Retrieves the current version of visual studio. This will be use to create# the url of the windows download file.
def find_version_visual_studio():
    global url_VS
    vs = None
    html_content = requests.get(url_VS, verify=False, proxies=proxy)
    hrefs = BeautifulSoup(html_content.content, "html.parser")
    if hrefs != -1:
        vs = hrefs.find("td")
        if vs is not None:
            vs = re.sub("<td>", "", str(vs))
            vs = re.sub("<\/td>", "", str(vs))
    return vs


# Goes through linux download process
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
def windows(html, download):
    # Global variable declaration
    global path_name
    # changes the file name
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
