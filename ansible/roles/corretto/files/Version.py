import requests
from bs4 import BeautifulSoup
import re
import urllib3


class Version:
    site_url = ""
    search_for_url = ""
    proxy = {}
    patch = ""

    # Version constructor. Initializes instance fields
    # @param String website
    # @param String version
    # @param Boolean new
    # @param String proxy
    # @param struct_time time_checks
    def __init__(self, su, sfu, pr, pa):
        self.site_url = su
        self.search_for_url = sfu
        self.proxy = pr
        self.patch = pa

    # Opens base website and retrieves the first url with the version
    # splits that link in order to retrieve the version number. stores
    # the version in the global variable new_version.
    def get_version(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # URL of corretto update downloads
        if self.proxy == {""}:
            html_content = requests.get(self.site_url)
        else:
            html_content = requests.get(self.site_url, verify=False, proxies=self.proxy)
        # Parses website for the html content
        links = BeautifulSoup(html_content.content, "html.parser")
        # Checks for errors
        if links != -1:
            # Retrieves the first URL with version information
            url = links.find(href=re.compile(self.search_for_url))
            # checks for error
            if url is not None:
                if self.patch == "corretto":
                    # splits the URL
                    url_split = str(url).split('/')
                    # version information should be in array position 3 based on naming conventions
                    return url_split[3]
                if self.patch == "apache":
                    # splits the URL
                    url_split = str(url).split('-')
                    new_version = url_split[1].split(".tar")
                    # version information should be in array position 3 based on naming conventions
                    return new_version[0]
                if self.patch == "linux":
                    url_split = str(url).split('-')
                    return url_split[2]
