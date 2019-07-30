from bs4 import BeautifulSoup
from Email import EmailGenerator
from Version import Version
import requests
import re
import time
import os
import urllib3

previous_version = 0  # keeps track of previous version to
# check if it has changed
new_version = 0  # used to compare the two versions
url_beginning = "https://d3pxv6yz143wms.cloudfront.net/"  # for simplicity
corretto_version = 8  # specifies if it is 11 or 8
time_checked = 0


# Reads and writes time and version information to and from a file. Compares the new version,
# with the old. Calls download function to write files to computer. Runs main
# twice for corretto 8 and 11.
def main():
    # Declares global variables locally
    global new_version
    global previous_version
    global corretto_version
    global time_checked
    i = 0
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Runs process twice for 8 and 11
    while i < 2:
        new = False
        # Reads in old version
        get_old_version_and_time()
        # Retrieves new version
        version()
        # Checks to see if the version has updated since last download
        if new_version != previous_version:
            # Writes necessary files to computer
            download()
            new = True
            EmailGenerator("https://alas.aws.amazon.com/alas2.html", new_version, new,
                           {"https": "https://...."}, time_checked).get_security_info()
            time_checked = time.localtime(time.time())
        else:
            # Generates Email file for the user
            EmailGenerator("https://alas.aws.amazon.com/alas2.html", new_version, new,
                           {"https": "https://...."}, time_checked).get_security_info()
        # Updates time_checked to current time
        # Updates the old_version file to contain the new version information
        update_file_new_version_and_time()
        i += 1
        corretto_version = 11


# Reads old_version file in order to check if new_version and old_version
# match. Also retrieves old time stamp
def get_old_version_and_time():
    global corretto_version
    global previous_version
    global time_checked
    try:
        ov_file = open('/etc/ansible/roles/corretto/files/old_version' + str(corretto_version) + '.txt',
                       'r')
        previous_version = ov_file.readline().rstrip('\n')
        time_tuple = (ov_file.readline())
        # Turns string in to tuple format
        time_checked = time.struct_time(int(x) for x in time_tuple.split(","))
        ov_file.close()
    except IOError:
        print("File old_version" + str(corretto_version) + ".txt not in directory while getting version")


# Writes the new version number to the old_version file. Allows us to keep
# track of version changes
def update_file_new_version_and_time():
    global corretto_version
    global new_version
    global time_checked
    try:
        ov_file = open('/etc/ansible/roles/corretto/files/old_version' + str(corretto_version) + '.txt',
                       'w')
        ov_file.write(new_version + "\n")
        # Turns tuple of ints into string
        ov_file.write(str(time_checked.tm_year) + ", " + str(time_checked.tm_mon) + ", " + str(time_checked.tm_mday)
                      + ", " + str(time_checked.tm_hour) + ", " + str(time_checked.tm_min) + ", " +
                      str(time_checked.tm_sec) + ", " + str(time_checked.tm_wday) + ", " + str(time_checked.tm_yday)
                      + ", " + str(time_checked.tm_isdst))
        ov_file.close()
    except IOError:
        print("File old_version" + str(corretto_version) + ".txt not in directory while getting new version file")


# Opens base website and retrieves the first url with the version
# splits that link in order to retrieve the version number. stores
# the version in the global variable new_version.
def version():
    global corretto_version
    global new_version
    global url_beginning
    # URL of corretto update downloads
    url = "https://docs.aws.amazon.com/corretto/latest/corretto-" + str(corretto_version) + "-ug/downloads-list.html"
    new_version = Version(url, url_beginning, {"https": "https://...."},
                          "corretto").get_version()


# Searches the amazon corretto website for all relevant files. Parses for file names
# to use as specifiers. Downloads file onto the host computer.
def download():
    success = False
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
            if link != -1:
                url = link['href']
                if url != -1:
                    # Rules out irrelevant files on the website
                    if "deb" not in str(url) and "msi" not in str(url) and "jre" not in str(url) and "sig" not in str(
                            url) and "aarch64" not in str(url) and "amzn2" not in str(url) and (("windows" in str(url)
                                or "linux" in str(url)) or "rpm" in str(url)):
                        # Retrieves and formats file name
                        retrieving_name = str(link).split(">")
                        file_name = retrieving_name[1]
                        file_name = file_name[:-3]
                        downloaded_file = requests.get(url)
                        # Opens and writes new file to computer
                        cv = str(corretto_version)
                        try:
                            # Designated path to downloaded directory
                            path_name = "/downloaded/"
                            # Checks to see if the extracted link is a linux file
                            if "linux" in file_name or "rpm" in file_name:
                                # Checks to see if the linux directory in downloaded
                                if os.path.exists(path_name + cv + "/linux/"):
                                    # Creates the tar and rpm files
                                    with open(path_name + cv + "/linux/" + file_name, 'wb') as new_file:
                                        new_file.write(downloaded_file.content)
                                else:
                                    # Creates linux directory in downloaded directory
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
