wifi-heatmap
============

Tool for Generating wifi coverage heatmaps for a redpin database using Python.

This implementation will extend the original wifi-heatmap from [beaugunderson](http://github.com/beaugunderson) and use it to visualize data acquired with the [RedPin](http://redpin.org) Indoor Localization System from [ETH Zurich](http://www.ethz.ch/).

It will need NumPy, SciPy and matplotlib in order to draw the heatmap. In addition to that it needs mysql-python for it to connect to the database and get the rssi values from there.
