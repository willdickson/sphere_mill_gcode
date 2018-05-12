import numpy as np
from utility import get_num_steps
from utility import get_equal_angle_steps


def get_toolpath_radius_from_step(diam_sphere, diam_tool, step, margin):
    """
    Calculates the radius of the toolpath annulus for milling a sphere as a
    function of the stepdown where the stepdown is in [0,-radius_sphere].
    Assmues a ball nose endmill with diameter tool_diam.
    """
    diam_effective = diam_sphere + 2*margin
    tool_dist = 0.5*diam_effective + 0.5*diam_tool
    radius_cut = np.sqrt(tool_dist**2 - (tool_dist + (step-margin))**2)
    return radius_cut


def get_toolpath_annulus_data(params):
    """
    Returns the radius and z step of the toolpath machining the top half of a
    sphere using annular cutting paths with  ball nose endmill.

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
    toolpath_data = []
    for step in step_array:
        toolpath_radius = get_toolpath_radius_from_step(diam_sphere, diam_tool, step, margin)
        toolpath_data.append({'radius': toolpath_radius, 'z_step': step+offset})
    return toolpath_data



    



    




