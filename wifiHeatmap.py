from __future__ import division

import tabular as tb
import numpy as np
import matplotlib.pyplot as pp

from mpl_toolkits.axes_grid1 import AxesGrid
from scipy.interpolate import Rbf
from pylab import imread
from matplotlib.offsetbox import AnchoredText
from matplotlib.patheffects import withStroke


class heatmap:

    resolution_scale = 4

    def __init__(self, layout, data):
        self.layout = imread(layout)
        self.csv = tb.tabarray(SVfile=data)
        self.aps = self.csv.dtype.names[3:]
        self.image_width = len(self.layout[0])
        self.image_height = len(self.layout)

        self.num_x = self.image_width / self.resolution_scale
        self.num_y = self.num_x / (self.image_width / self.image_height)

        x = np.linspace(0, self.image_width, self.num_x)
        y = np.linspace(0, self.image_height, self.num_y)

        self.gx, self.gy = np.meshgrid(x, y)
        self.gx, self.gy = self.gx.flatten(), self.gy.flatten()

        self.levels = [-85, -80, -75, -70, -65, -60, -55, -50, -45, -40, -35, -30, -25]

    def grid_plots(self, beacons):

        def _add_inner_title(ax, title, loc, size=None, **kwargs):

            if size is None:
                size = dict(size=pp.rcParams['legend.fontsize'])

            at = AnchoredText(title, loc=loc, prop=size, pad=0., borderpad=0.5, frameon=False, **kwargs)

            at.set_zorder(200)
            ax.add_artist(at)
            at.txt._text.set_path_effects([withStroke(foreground="w", linewidth=3)])
            return at

        f = pp.figure()
        f.suptitle("Individual AP RSSI")

        # Adjust the margins and padding
        f.subplots_adjust(hspace=0.1, wspace=0.1, left=0.05, right=0.95, top=0.85, bottom=0.15)

        # Create a grid of subplots using the AxesGrid helper
        image_grid = AxesGrid(f, 111, nrows_ncols=(2, 3), axes_pad=0.1, label_mode="1", share_all=True, cbar_location="right", cbar_mode="single", cbar_size="3%")

        # truncate too much beacons
        if beacons > 6:
            beacons = beacons[:6]

        for beacon, i in zip(beacons, xrange(len(beacons))):
            # Hide the axis labels
            image_grid[i].xaxis.set_visible(False)
            image_grid[i].yaxis.set_visible(False)

            # Interpolate the data
            rbf = Rbf(self.csv['Drawing X'], self.csv['Drawing Y'], self.csv[beacon], function='linear')
            z = rbf(self.gx, self.gy)
            z = z.reshape((self.num_y, self.num_x))

            # Render the interpolated data to the plot
            image = image_grid[i].imshow(z, vmin=-85, vmax=-25, extent=(0, self.image_width, self.image_height, 0), cmap='RdYlBu_r', alpha=1)
            image_grid[i].imshow(self.layout, interpolation='bicubic', zorder=100)

        # Setup the data for the colorbar and its ticks
        image_grid.cbar_axes[0].colorbar(image)
        image_grid.cbar_axes[0].set_yticks(self.levels)

        # Add inset titles to each subplot
        for ax, im_title in zip(image_grid, beacons):
            t = _add_inner_title(ax, "Beacon %s" % im_title, loc=3)
            t.patch.set_alpha(0.5)

        pp.show()

    def max_plot(self, beacons=None):
        # Get the maximum RSSI seen for each beacon
        aps = []
        for a in self.aps:
            aps.append(a)

        if beacons is None:
            max_rssi = [max(i) for i in self.csv[aps]]
        else:
            max_rssi = [max(i) for i in self.csv[beacons]]

        pp.title("Maximum RSSI seen for each beacon")

        # Interpolate the data
        rbf = Rbf(self.csv['Drawing X'], self.csv['Drawing Y'], max_rssi, function='linear')

        z = rbf(self.gx, self.gy)
        z = z.reshape((self.num_y, self.num_x))

        # Render the interpolated data to the plot
        image = pp.imshow(z, vmin=-85, vmax=-25, extent=(0, self.image_width, self.image_height, 0), cmap='RdYlBu_r', alpha=1)

        pp.colorbar(image)
        pp.imshow(self.layout, interpolation='bicubic', zorder=100)
        pp.show()

if __name__ == "__main__":
    print "main"
    wh = wifiHeatmap('input/layout2.png', 'input/mapping2.csv')
    # wh.grid_plots(['64:70:02:3e:9f:63', '64:70:02:3e:aa:11', '64:70:02:3e:aa:d9', '64:70:02:3e:aa:ef'])
    wh.max_plot(['64:70:02:3e:9f:63', '64:70:02:3e:aa:11', '64:70:02:3e:aa:d9', '64:70:02:3e:aa:ef'])
