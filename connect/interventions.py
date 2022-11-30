# -*- coding: utf-8 -*-
"""
    Convert intervention files into API requests.
"""

##### IMPORTS #####
# Standard imports
from __future__ import annotations
import enum
import logging
import pathlib
import datetime as dt

# Third party imports
import geopandas as gpd
import numpy as np
import requests

# Local imports

##### CONSTANTS #####
LOG = logging.getLogger(__name__)
NETWORK_CRS = "EPSG:4326"
PT_URL = "https://thick-humans-tap-34-89-73-233.loca.lt/"

##### CLASSES #####
class SimpleMode(enum.Enum):
    WALK = "walk"
    CYCLE = "cycle"

    @staticmethod
    def mode_lookup() -> dict[int, SimpleMode]:
        return {
            SimpleMode.WALK: 1,
            SimpleMode.CYCLE: 2,
        }

    def get_mode_num(self) -> int:
        return self.mode_lookup()[self]


##### FUNCTIONS #####
def route_interventions(file: pathlib.Path, layer: str) -> dict[SimpleMode, gpd.GeoDataFrame]:
    interventions = gpd.read_file(file, layer=layer)
    interventions = interventions.loc[:, ["link_name", "mode", "geometry"]]

    interventions = interventions.to_crs(NETWORK_CRS)

    mode_interventions = {}
    for m in SimpleMode:
        gdf = interventions.loc[interventions["mode"] == m.get_mode_num()]
        if len(gdf) > 0:
            mode_interventions[m] = gdf

    return mode_interventions

def seconds_since_midnight(time: dt.time) -> int:
    return time.hour * 3600 + time.minute * 60 + time.second

def request_simple_interventions(geometries: gpd.GeoDataFrame, mode: SimpleMode):
    payload = {
        "lat_long_pairs": geometries.geometry.apply(lambda x: list(x.coords)).tolist(),
        "mode_simpler": mode.value,
        "TripStartHours": 8,
        "return_home": False,
        "max_travel_time": 3600,
        "geography_level": "lsoa",
        "arrival_times": (seconds_since_midnight(dt.time(8)),),
        "departure_times": (seconds_since_midnight(dt.time(8)),),
    }

    res = requests.post(PT_URL, json=payload)
    print(res.text)

if __name__ == "__main__":
    routes = route_interventions(r"C:\Users\UKMJB018\OneDrive - WSP O365\Projects\DfT Connectivity Hackathon\mersey_bridge.gpkg", "mersey_bridge")

    for m, geoms in routes.items():
        request_simple_interventions(geoms, m)
