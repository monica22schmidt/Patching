import requestsfrom bs4 
import BeautifulSoup
import re
import urllib3

# Version Class:
#
# This class searches for version information given specfic parameters.
# Each website has slightly different requirements, but overall structure is the 
# same.
# @author Monica Schmidt
class Version:    
    site_url = ""    
    search_for_url = ""    
    proxy = {}    
    patch = ""    
    
    # Version constructor. Initializes instance fields    
    # @param website    
    # @param version    
    # @param proxy    
    # @param new    
    def __init__(self, su, sfu, pr, pa):        
        self.site_url = su        
        self.search_for_url = sfu        
        self.proxy = pr        
        self.patch = pa    
        
    # Opens the base website and retrieves the first url with the version     
    # information. It then splits that link in order to retrieve the version     
    # number. Then it returns the version number.    
    # @return the latest version number    
    def get_version(self):    
        
        # Disables warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # URL of corretto update downloads
        if self.proxy == "":            
            html_content = requests.get(self.site_url)        
        else:            
            html_content = requests.get(self.site_url, verify=False, proxies=self.proxy)  
            
        # Parses website for the html content        
        links = BeautifulSoup(html_content.content, "html.parser")   
        
        # Checks for errors        
        if links != -1:   
            
            # Retrieves the first URL with version information            
            url = links.find(href=re.compile(self.search_for_url))   
            
            # Checks for errors            
            if url is not None:   
                
                # Corretto specifications                
                if self.patch == "corretto":
                    
                    # Splits the URL                    
                    url_split = str(url).split('/')
                    
                    # Version information should be in array position 3,                    
                    # based on naming conventions                    
                    return url_split[3]    
                    
                # Apache specifications                
                if self.patch == "apache":   
                    
                    # Splits the URL                    
                    url_split = str(url).split('-')       
                    
                    # Version information should be in array position 1,                    
                    # based on naming conventions                    
                    new_version = url_split[1].split(".tar")   
                    
                    # Version information now in array position 0                    
                    return new_version[0] 
                    
                # Repo specifications                
                if self.patch == "repo":
                    
                    # Splits the URL 
                    url_split = str(url).split('-') 
                    
                    # Version information should be in array position 2,                    
                    # based on naming conventions    
                    return url_split[2]
