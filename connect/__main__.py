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

DUMMY_REQUEST = {'lat_long_pairs': (((51.51966979, -0.09087451), (51.51850755, -0.092354771)),),
                 'mode_simpler': 'walk',
                 'TripStartHours': 8,
                 'return_home': False,
                 'max_travel_time': 3600,
                 'arrival_times': 8,
                 'departure_times': 6,
                 'geography_level': 'lsoa'}

##### CLASSES #####

##### FUNCTIONS #####
def main():
    print("Requesting")
    res = requests.post(DUMMY_PT_URL, timeout=10000, json=DUMMY_REQUEST)
    print(res.text)

if __name__ == "__main__":
    main()
