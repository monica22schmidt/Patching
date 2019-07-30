from Version import Version
import sys


# Used to retrieve the version number from the middleware repo. This is used to create the old version directory
def main(argv):
    version = Version("http://webaddress/" + argv + "/", "amazon", {},
                      "linux").get_version()
    print(argv)
    print(version)


# argv for 11 or 8
if len(sys.argv) == 2:
    main(sys.argv[1])
