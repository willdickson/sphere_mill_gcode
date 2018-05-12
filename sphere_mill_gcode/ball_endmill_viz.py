from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt

import  ball_endmill 
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
    plot_circle(cx_sphere, cy_sphere, 0.5*diam_sphere)
    plot_circle(cx_sphere, cy_sphere, 0.5*diam_sphere+margin,'c')
    plt.plot([-diam_sphere,diam_sphere],[cy_sphere, cy_sphere], 'k')
    plt.plot([-diam_sphere,diam_sphere],[cy_sphere+0.5*tab_thickness, cy_sphere+0.5*tab_thickness], 'b')
    plt.plot([-diam_sphere,diam_sphere],[cy_sphere-0.5*tab_thickness, cy_sphere-0.5*tab_thickness], 'b')

    # Plot ball nose end mills
    toolpath_annulus_data = ball_endmill.get_toolpath_annulus_data(params)
    for data in toolpath_annulus_data:
        for sgn in (1,-1):
            radius = sgn*data['radius']
            z_step = data['z_step']
            plot_circle(radius, z_step+0.5*diam_tool, 0.5*diam_tool,color='g')
            plt.plot([radius], [z_step+0.5*diam_tool], '.g')
            plt.plot([radius], [z_step], 'xg')

# -----------------------------------------------------------------------------
if __name__ == '__main__':


    params = { 
            'diam_sphere'   : mm_to_inch(12.0),
            'diam_tool'     : 1.0/8.0 ,
            'margin'        : 0.1,
            'step_size'     : 0.01,
            'tab_thickness' : 0.01,
            'offset'        : -0.1,
            }
    

    fig_num = 1
    plt.figure(fig_num)
    plot_spheremill_toolpos(params) 
    plt.axis('equal')
    plt.grid('on')
    plt.show()


