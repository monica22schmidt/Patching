import requests
from bs4 import BeautifulSoup
import re


# Email Class:
#
# Retrieves security information about the current patch. It also outputs the 
# security information, so it can be sent to our users in an email.
# @author Monica Schmidt
class Email:
    Website = ""
    Version = ""
    Proxy = {}
    New = False

    # Email Constructor:
    #
    # Assigns values to Website, Version, Proxy, and New, based on the apache 
    # patch information. This is called in the patch file
    # @param website, url of security page
    # @param version, the version number to look for
    # @param proxy, the proxy server for the security page
    # @param new, boolean as to whether or not the patch is new
    def __init__(self, website, version, proxy, new):
        self.New = new
        self.Website = website
        self.Version = version
        self.Proxy = proxy

    # Get Security Info Method:
    #
    # Retrieves security information based on the website and the patch version.
    # Outputs the information to send to apache users.
    def get_security_info(self):
        
        # Loads html content of the security page into a variable
        html_content = requests.get(self.Website, verify=False,
                                    proxies=self.Proxy)
                                    
        # Turns html into human readable format
        html = BeautifulSoup(html_content.content, "html.parser")
        
        # Gets the most recent version number for the latest security patch
        security = html.find(id=self.Version)
        
        # Starts printing. It will email user even if it is not a security patch
        # Email Heading
        print("Apache " + self.Version[:3] + "\n")
        print("-------------\n")
        
        # Evaluates if there was a new patch
        if self.New:
            print("Congrats! A New Patch Is Available! \n")
            print("New Patch Number: " + self.Version + " \n")
        else:
            print("No New Patch Available \n")
            print("Current Version: " + self.Version + " \n")
            
        # Evaluates if we have a security patch
        if security:
            print("Security Patch: yes \n")
            print("Security Information: \n")
            
            # The first DL tag has all relevant information
            info = html.find("dl")
            
            # Need the a tag to get the CVE url and dt for the security blurb
            info = info.findAll(["dt", "a"])
            
            # Removes all tag syntax, skips dt and a tags
            cleaned = re.compile('<(?!a href=)(?!/dt>).*?>')
            email = re.sub(cleaned, "", str(info))
            
            #Removes end of dt tag
            email = re.sub(re.compile('<\/dt>.+?(?=,),'), "\n", email)
            email = re.sub(re.compile('<\/dt>.+?(?=])]'), "\n", email)
            
            # Removes all unwanted syntax
            email = str(email).replace("[", "").replace("\\n","\n").replace("(<a href=\"", "").replace("\">", " ").replace(")", "")
            print(email)
            
        else:
            print("Security Patch: no")


