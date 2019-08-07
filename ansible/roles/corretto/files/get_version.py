from Version import Version
import sys


# Used to retrieve the version number from the  repo. 
# This is used to create the old version directory.
def main(argv):
    
    # Calls Version class
    version = Version("http://..." + argv + "/", "amazon", {},
                      "repo").get_version()
    # Prints the retrieved information to be used when making  repo
    print(argv)
    print(version)


# argv for 11 or 8
if len(sys.argv) == 2:
    main(sys.argv[1])
