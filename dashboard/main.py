# -*- coding: utf-8 -*-
"""
    module_description
"""

##### IMPORTS #####
# Standard imports
import datetime as dt
import logging
import pprint

# Third party imports
from bokeh import tile_providers, models, plotting, palettes, layouts
import requests
import pyproj
import pandas as pd
import geopandas as gpd

# Local imports

##### CONSTANTS #####

lsoas_shp = '/path/to/file.shp'
map_html = '/path/to/map.html'

LOG = logging.getLogger(__name__)
AC_URL = "https://dirty-sloths-guess-34-89-73-233.loca.lt/"

##### CLASSES #####
class TestDashboard:
    def __init__(self) -> None:
        p = plotting.figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
        p.border_fill_color = 'black'
        p.background_fill_color = 'black'
        p.outline_line_color = None
        p.grid.grid_line_color = None

        # add a text renderer to the plot (no data yet)
        r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
                text_baseline="middle", text_align="center")

        self.i = 0

        self.ds = r.data_source

        # create a callback that adds a number in a random location

        # add a button widget and configure with the call back
        button = models.Button(label="Press Me")
        button.on_event('button_click', self.callback)

        # put the button and plot in a layout and add to the document
        plotting.curdoc().add_root(layouts.column(button, p))

    def callback(self):
        # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data['x'] = self.ds.data['x'] + [random()*70 + 15]
        new_data['y'] = self.ds.data['y'] + [random()*70 + 15]
        new_data['text_color'] = self.ds.data['text_color'] + [palettes.RdYlBu3[self.i % 3]]
        new_data['text'] = self.ds.data['text'] + [str(self.i)]
        self.ds.data = new_data

        self.i += 1

class DrawDashboard():

    def __init__(self) -> None:
        self.source = models.ColumnDataSource(dict(xs=[], ys=[]))

        p = plotting.figure(x_range=(-342169, -323569), y_range=(7055344, 7066390),
           x_axis_type="mercator", y_axis_type="mercator")
        p.add_tile(tile_providers.get_provider(tile_providers.CARTODBPOSITRON))
        r = p.multi_line("xs", "ys", source=self.source)
        tool = models.PolyDrawTool(renderers=[r])
        p.add_tools(tool)

        columns = [
            models.TableColumn(field="xs", title="X"),
            models.TableColumn(field="ys", title="Y"),
        ]
        dt = models.DataTable(columns=columns, source=self.source)
        
        but = models.Button(label="Click me")
        but.on_click(self.button_click)

        plotting.curdoc().add_root(layouts.column(but, p, dt))
        
        self.boundary_shp = gpd.read_file(lsoas_shp)[['LSOA21CD', 'geometry']]

    def button_click(self):        
        df = self.source.to_df()

        t = pyproj.Transformer.from_crs("epsg:3857", "epsg:4326")
        lat_long = []
        for _, row in df.iterrows():
            xy = t.transform(row["xs"], row["ys"])
            print(xy)
            lat_long.append(list(zip(*xy))) 
        
        payload = {
            "lat_long_pairs": lat_long,
            "mode_simpler": "walk",
            "TripStartHours": 8,
            "return_home": False,
            "max_travel_time": 3600,
            "geography_level": "lsoa",
            "arrival_times": (seconds_since_midnight(dt.time(8)),),
            "departure_times": (seconds_since_midnight(dt.time(8)),),
        }
        pprint.pp(payload)

        res = requests.post(AC_URL, json=payload, verify=False)
        api_output = pd.DataFrame(res.json())
        
        
        # Join to gdf
        geodataframe = self.boundaries.merge(api_output, left_on='LSOA21CD', right_on='lsoa', how='inner')
        
        # Create map
        m = geodataframe.explore(column='overall_diff', cmap='cividis', scheme='Quantiles', k=5)
        
        # export to html
        m.save(map_html)
        
        
     

def seconds_since_midnight(time: dt.time) -> int:
    return time.hour * 3600 + time.minute * 60 + time.second


DrawDashboard()