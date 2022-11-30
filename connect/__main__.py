# -*- coding: utf-8 -*-
"""
    module_description
"""

##### IMPORTS #####
# Standard imports
import logging
import urllib

# Third party imports
import requests

# Local imports

##### CONSTANTS #####
LOG = logging.getLogger(__name__)
DUMMY_PT_URL = "https://free-rivers-glow-34-89-73-233.loca.lt"
PT_URL = "https://thick-humans-tap-34-89-73-233.loca.lt/"

##### CLASSES #####

##### FUNCTIONS #####
def main():
    print("Requesting")
    res = requests.get("https://www.google.co.uk/")
    print(res.text)
    res = requests.post(DUMMY_PT_URL, timeout=10000, verify=False)
    print(res.text)

if __name__ == "__main__":
    main()
