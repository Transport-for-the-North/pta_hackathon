# -*- coding: utf-8 -*-
"""
    module_description
"""

##### IMPORTS #####
# Standard imports
import logging

# Third party imports
from bokeh import tile_providers, models, plotting, palettes, layouts
from random import random

# Local imports

##### CONSTANTS #####
LOG = logging.getLogger(__name__)

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

    def button_click(self):        
        print(f"Data is:\n{self.source.to_df()}")


DrawDashboard()
