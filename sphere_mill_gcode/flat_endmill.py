from __future__ import print_function
import numpy as np
from utility import get_num_steps
from utility import get_equal_angle_steps


def get_toolpath_radius_from_step(diam_sphere, diam_tool, step, margin):
    """
    Calculates the radius of the toolpath annulus for milling a sphere as a
    function of the step where the step is in [0,-radius_sphere].
    Assmues a flat nose endmill with diameter tool_diam.
    """

    radius_effective = 0.5*diam_sphere + margin
    radius_tool = 0.5*diam_tool
    return np.sqrt(radius_effective**2 - (radius_effective + step-margin)**2) + radius_tool 

def get_toolpath_annulus_data(params): 
    """
    Returns the radius and z step of the toolpath machining the top half of a
    sphere using annular cutting paths with  flat nose endmill.

    Arguments:
        diam_sphere      =  diameter of sphere
        diam_tool        =  diameter of the ball nose end mill
        tab_thickness    =  thickness of tab remaining between top and bottom half of shpere
        step_size        =  (approx) size of vertical steps for annulus cuts.
        margin           =  margin of material on sphere (for roughing etc.)
    """
    # Extract params
    diam_sphere = params['diam_sphere']
    diam_tool = params['diam_tool']
    tab_thickness = params['tab_thickness']
    step_size = params['step_size']
    margin = params['margin']
    offset = params['offset']

    # Get tool path data
    num_steps = get_num_steps(diam_sphere, tab_thickness, step_size, margin)
    step_array = get_equal_angle_steps(diam_sphere, tab_thickness, num_steps, margin)
    step_array = np.concatenate(([margin], step_array))
    toolpath_data = []
    for i, step in enumerate(step_array):
        if i == 0:
            toolpath_radius = 0.25*diam_tool 
        else:
            toolpath_radius = get_toolpath_radius_from_step(diam_sphere, diam_tool, step, margin)
        toolpath_data.append({'radius': toolpath_radius, 'z_step': step+offset})
    return toolpath_data

