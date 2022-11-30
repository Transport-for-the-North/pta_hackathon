# -*- coding: utf-8 -*-
"""
    module_description
"""

##### IMPORTS #####
# Standard imports
import datetime as dt
import logging
import os
import pprint

# Third party imports
from bokeh import tile_providers, models, plotting, palettes, layouts
import requests
import pyproj
import pandas as pd
import geopandas as gpd
from shapely import geometry

# Local imports

##### CONSTANTS #####

lsoas_shp = r"C:\Users\UKMJB018\OneDrive - WSP O365\Projects\DfT Connectivity Hackathon\lsoa4326\EW_LSOA_boundaries_dec21_LSOA_2021_EW_BFE_V5.shp"
map_html = r"C:\Users\UKMJB018\OneDrive - WSP O365\Projects\DfT Connectivity Hackathon\map.html"

LOG = logging.getLogger(__name__)
AC_URL = "https://dirty-sloths-guess-34-89-73-233.loca.lt/"

##### CLASSES #####
class TestDashboard:
    def __init__(self) -> None:
        p = plotting.figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
        p.border_fill_color = "black"
        p.background_fill_color = "black"
        p.outline_line_color = None
        p.grid.grid_line_color = None

        # add a text renderer to the plot (no data yet)
        r = p.text(
            x=[],
            y=[],
            text=[],
            text_color=[],
            text_font_size="26px",
            text_baseline="middle",
            text_align="center",
        )

        self.i = 0

        self.ds = r.data_source

        # create a callback that adds a number in a random location

        # add a button widget and configure with the call back
        button = models.Button(label="Press Me")
        button.on_event("button_click", self.callback)

        # put the button and plot in a layout and add to the document
        plotting.curdoc().add_root(layouts.column(button, p))

    def callback(self):
        # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data["x"] = self.ds.data["x"] + [random() * 70 + 15]
        new_data["y"] = self.ds.data["y"] + [random() * 70 + 15]
        new_data["text_color"] = self.ds.data["text_color"] + [
            palettes.RdYlBu3[self.i % 3]
        ]
        new_data["text"] = self.ds.data["text"] + [str(self.i)]
        self.ds.data = new_data

        self.i += 1


class DrawDashboard:
    X_RANGE = (-342169, -323569)
    Y_RANGE = (7055344, 7066390)

    def __init__(self) -> None:
        self.source = models.ColumnDataSource(dict(xs=[], ys=[]))

        p = plotting.figure(
            x_range=self.X_RANGE,
            y_range=self.Y_RANGE,
            x_axis_type="mercator",
            y_axis_type="mercator",
            sizing_mode="stretch_both",
        )
        p.add_tile(tile_providers.get_provider(tile_providers.CARTODBPOSITRON))
        r = p.multi_line("xs", "ys", source=self.source)
        tool = models.PolyDrawTool(renderers=[r])
        p.add_tools(tool)

        self.load_lsoas()
        # p.multi_polygons(
        #     xs="xs", ys="ys", color="colour", alpha=0.5, source=self.lsoa_source
        # )

        dt = models.DataTable(
            columns=[
                models.TableColumn(field="xs", title="X"),
                models.TableColumn(field="ys", title="Y"),
            ],
            source=self.source,
        )
        lsoa_dt = models.DataTable(
            columns=[models.TableColumn(field="LSOA21CD", title="LSOA21CD")],
            # source=self.lsoa_source,
        )

        but = models.Button(label="Update Graph", sizing_mode="stretch_both")
        but.on_click(self.button_click)

        self.mode_select = models.Select(
            title="Mode",
            value="walk",
            options=["walk", "cycle"],
            sizing_mode="stretch_both",
        )

        selections = layouts.row(but, self.mode_select, sizing_mode="stretch_width")
        outputs = models.Tabs(
            tabs=[
                models.Panel(child=p, title="Map"),
                models.Panel(child=dt, title="New Links"),
                models.Panel(child=lsoa_dt, title="LSOA Data"),
            ],
        )

        plotting.curdoc().add_root(
            layouts.column(selections, outputs, sizing_mode="stretch_both")
        )

    def load_lsoas(self):
        self.boundaries = gpd.read_file(lsoas_shp)[["LSOA21CD", "geometry"]]

        # Drop multipolygons
        self.boundaries = self.boundaries.loc[self.boundaries.geometry.geom_type == "Polygon"]
        
        self.boundaries = self.boundaries.to_crs("epsg:4326")

        t = pyproj.Transformer.from_crs("epsg:3857", "epsg:4326")
        x, y = t.transform(self.X_RANGE, self.Y_RANGE)
        clip_poly = geometry.Polygon(
            [(y[0], x[0]), (y[1], x[0]), (y[1], x[1]), (y[1], x[0])]
        )
        self.boundaries = self.boundaries.clip(clip_poly)

        self.boundaries.loc[:, "colour"] = "black"

        self.lsoa_source = models.GeoJSONDataSource(geojson=self.boundaries.to_json())

    def update_lsoas(self, data: pd.DataFrame):
        updated = self.boundaries.merge(
            data, left_on="LSOA21CD", right_on="lsoa", how="inner"
        )
        # TODO Calculate colour based on cmap
        updated.loc[:, "colour"] = "yellow"

        self.lsoa_source = models.GeoJSONDataSource(updated.to_json())

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
            "mode_simpler": self.mode_select.value,
            "TripStartHours": 8,
            "return_home": False,
            "max_travel_time": 3600,
            "geography_level": "lsoa",
            "arrival_times": (seconds_since_midnight(dt.time(8)),),
            "departure_times": (seconds_since_midnight(dt.time(8)),),
        }

        res = requests.post(AC_URL, json=payload, verify=False)
        api_output = pd.DataFrame(res.json())

        # Join to gdf
        geodataframe = self.boundaries.merge(
            api_output, left_on="LSOA21CD", right_on="lsoa", how="inner"
        )

        # Create map
        m = geodataframe.explore(
            column="overall_diff", cmap="cividis", scheme="Quantiles", k=5
        )

        # export to html
        m.save(map_html)
        os.startfile(map_html)


def seconds_since_midnight(time: dt.time) -> int:
    return time.hour * 3600 + time.minute * 60 + time.second


DrawDashboard()
