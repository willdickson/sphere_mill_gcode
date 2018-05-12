from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt

import flat_endmill
from utility import mm_to_inch
from utility import plot_circle

def plot_spheremill_toolpos(params): 

    # Extract parameters
    diam_tool = params['diam_tool']
    diam_sphere = params['diam_sphere']
    tab_thickness = params['tab_thickness']
    offset = params['offset']
    margin = params['margin']

    # Plot sphere
    cx_sphere = 0.0
    cy_sphere = -0.5*diam_sphere + offset
    plot_circle(cx_sphere, cy_sphere, 0.5*diam_sphere,'r')
    plot_circle(cx_sphere, cy_sphere, 0.5*diam_sphere+margin,'c')
    plt.plot([-diam_sphere,diam_sphere],[cy_sphere, cy_sphere], 'k')
    plt.plot([-diam_sphere,diam_sphere],[cy_sphere+0.5*tab_thickness, cy_sphere+0.5*tab_thickness], 'b')
    plt.plot([-diam_sphere,diam_sphere],[cy_sphere-0.5*tab_thickness, cy_sphere-0.5*tab_thickness], 'b')

    # Plot flat nose endmill
    toolpath_annulus_data = flat_endmill.get_toolpath_annulus_data(params)
    for i, data in enumerate(toolpath_annulus_data):
        z_step = data['z_step']
        for sgn in (1,-1):
            radius = sgn*data['radius']
            plt.plot([radius], [z_step], 'xg')
            plot_flat_tool(radius,z_step,diam_tool,2*diam_tool,'g')

def plot_flat_tool(x,z,diam_tool,height_tool,color='b'):
    x0, z0 = x - 0.5*diam_tool, z
    x1, z1 = x + 0.5*diam_tool, z
    x2, z2 = x + 0.5*diam_tool, z + height_tool
    x3, z3 = x - 0.5*diam_tool, z + height_tool
    plt.plot([x0,x1,x2,x3,x0],[z0,z1,z2,z3,z0],color)


# --------------------------------------------------------------------------------------------

if __name__ == '__main__':

    params = { 
            'diam_sphere'   : mm_to_inch(12.0),
            'diam_tool'     : 1.0/8.0 ,
            'margin'        : 0.1,
            'step_size'     : 0.01,
            'tab_thickness' : 0.01,
            'offset'        : -0.1,
            }

    plot_spheremill_toolpos(params)
    plt.axis('equal')
    plt.grid('on')
    plt.show()
