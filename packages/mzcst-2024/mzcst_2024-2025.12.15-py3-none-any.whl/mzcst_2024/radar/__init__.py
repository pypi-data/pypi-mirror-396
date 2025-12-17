"""提供与`cst.radar`交互的接口。


`cst.radar` package

General Notes
====
This package provides functionalities to extract range and angle data as 
perceived by an automotive RADAR sensor from Studio simulations. Furthermore, 
plotting routines for conveniently calculating 2d range-angle maps are provided.

Note: To use this package please install the modules `scipy` (tested version: 
1.5.4), `numpy` (tested version: 1.19.5) and `matplotlib` (tested version: 
3.3.4) in your Python environment.

For the calculation of ranges two RADAR models are provided: A simple impulse 
based RADAR model and a linear FMCW-RADAR model. For a MIMO RADAR it is also 
possible to calculate angles based on phase differences between different 
channels of the MIMO RADAR. Finally, the range and angle calculation can be 
combined to a range-angle calculation for a MIMO RADAR.

"""

from . import (
    channel_tensor,
    coordinate_systems,
    plot,
    range_,
    range_angle,
    spectral_algorithms,
)
