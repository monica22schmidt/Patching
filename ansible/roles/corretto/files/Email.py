import requests
from bs4 import BeautifulSoup
import re
import time


# Email Class
# That retrieves security information about the current patch. It also creates a file to store the information to
# be sent to our users in an email.
class EmailGenerator:
    Website = ""
    Version = ""
    Updated = False
    Proxy = {}
    Last_Time_Checked = time.struct_time((2013, 7, 17, 21, 26, 3, 2, 198, 0))  # base time to search for

    # Email constructor. Initializes instance fields
    # @param String website
    # @param String version
    # @param Boolean new
    # @param String proxy
    # @param struct_time time_checks
    def __init__(self, website, version, new, proxy, time_checked):
        self.Website = website
        self.Version = version
        self.Updated = new
        self.Proxy = proxy
        self.Last_Time_Checked = time_checked

    # After time_stamp is received from the corretto security website it is reformatted into a struct_time type
    # @param String time_stamp
    # @return struct_time new_time_stamp
    def format_time(self, time_stamp):
        new_time_stamp = time.struct_time((int(time_stamp[0:4]), int(time_stamp[5:7]), int(time_stamp[8:10]),
                                           int(time_stamp[11:13]), int(time_stamp[14:16]),
                                           int(self.Last_Time_Checked.tm_sec),
                                           int(self.Last_Time_Checked.tm_wday), int(self.Last_Time_Checked.tm_yday),
                                           int(self.Last_Time_Checked.tm_isdst)))
        return new_time_stamp

    # Get Security Info Method
    # Retrieves security information based on the website, time stamp and the patch version. Puts this information into
    # a file to send to corretto users.
    def get_security_info(self):
        # Starts writing to file. It will email user even if it is not a security patch
        print(("Corretto " + self.Version[:2] + "\n").replace(".", ""))
        print("-------------\n")

        # Evaluates if there was a new patch
        if self.Updated:
            print("Congrats! A New Patch Is Available! \n")
            print("New Patch Number: " + self.Version + "\n")
        else:
            print("No New Patch Available \n")
            print("Current Version: " + self.Version + "\n")

        # Loads html content of the security page into a variable
        html_content = requests.get(self.Website, verify=False, proxies=self.Proxy)
        # Turns html into human readable format
        html = BeautifulSoup(html_content.content, "html.parser")
        # Desired info lives in <tr> tag
        tr_tag = html.findAll(re.compile("tr"))

        i = 2
        security = False
        # Retrieves the time stamp of the second item
        release_time = tr_tag[1].find("td")
        # Removes html format
        release_time = re.sub(re.compile('<.*?>'), "", str(release_time))
        time_stamp = self.format_time(release_time)
        # Calculates the sum of the date to see if last time checked is < current patch time stamp
        # Iterates through all the security patches that were created after the last time checked
        while time_stamp >= self.Last_Time_Checked and time_stamp is not None:
            # Looks for corretto specific patch
            corretto = re.search("([^ ]+)corretto+?</span>", str(tr_tag[i]))
            # Evaluates if the patch is a corretto patch
            if corretto is not None:
                # Removes the version number from the span tag
                version = tr_tag[i].find("span")
                version = str(version).split("-")
                version = version[2]
                # Checks if the version numbers are the same (8 or 11)
                if version == self.Version[0:2]:
                    # Retrieves security info page
                    url = tr_tag[i].find(href=re.compile("AL2"))
                    end = url.get('href')
                    self.Website = "https://alas.aws.amazon.com/" + end
                    security = True
                    break
                i += 1
            else:
                i += 1
                if i == len(tr_tag):
                    break
                else:
                    # Generates new time stamp based on td tag
                    time_stamp = tr_tag[i].find("td")
                    time_stamp = re.sub(re.compile('<.*?>'), "", str(time_stamp))
                    time_stamp = self.format_time(time_stamp)

        # Retrieves security details if a new security patch is found
        if security:
            print("Security Patch: yes \n")
            print("Security Information: \n")
            html_content = requests.get(self.Website, verify=False, proxies=self.Proxy)
            # Turns html into human readable format
            html = BeautifulSoup(html_content.content, "html.parser")
            # The ID severity has the security importance information
            severity = html.find(id="severity")
            # Removes html format
            severity = re.sub(re.compile('<.*?>'), "", str(severity))
            severity = re.sub(re.compile(" "), "", severity)
            severity = re.sub(re.compile("\n"), "", severity)
            # Adds the severity info to the email
            print(severity + "\n")
            # The ID issue_overview has the specifics on the issue including cve
            issue_info = html.find(id="issue_overview")
            # Removes all tag syntax skips p tag
            cleaned = re.compile('<(?!a href=)(?!/p>).*?>')
            email = re.sub(cleaned, "\n", str(issue_info))
            # Removes end of p tag
            email = re.sub(re.compile('">.*'), "", email)
            email = re.sub(re.compile('</p>.*'), "", email)
            # Removes target info
            email = re.sub(re.compile('" target.*'), "", email)
            # Removes all other unnecessary characters
            email = email.replace("[", "").replace("]", "").replace(",", "").replace("<a href=\"", "") \
                .replace("(", "").replace(")", "")
            print(email)
        else:
            print("Security Patch: no")
