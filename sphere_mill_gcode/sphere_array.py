from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
import py2gcode.gcode_cmd as gcode_cmd
import py2gcode.cnc_pocket as cnc_pocket

import flat_endmill
from utility import mm_to_inch


def create_roughing_program(params):

    prog = gcode_cmd.GCodeProg()
    prog.add(gcode_cmd.GenericStart())
    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.FeedRate(100.0))

    pos_list = pocket_centers(params)
    annulus_params = { 
            'diam_sphere'   : params['diam_sphere'],
            'diam_tool'     : params['roughing']['diam_tool'],
            'margin'        : params['roughing']['margin'],
            'step_size'     : params['roughing']['step_size'],
            'tab_thickness' : params['tab_thickness'],
            'center_z'      : params['center_z'],
            }
    toolpath_annulus_data = flat_endmill.get_toolpath_annulus_data(annulus_params)

    toolpath_radii = [data['radius'] for data in toolpath_annulus_data]
    max_radius = max(toolpath_radii) + 0.5*params['roughing']['diam_tool']
    first_step_z  = toolpath_annulus_data[0]['step_z']



    for pos in pos_list:
        # Remove material down to first step
        annulus_params = { 
                'centerX'        : pos['x'], 
                'centerY'        : pos['y'],
                'radius'         : max_radius,
                'thickness'      : max_radius,
                'depth'          : abs(first_step_z),
                'startZ'         : 0.0,
                'safeZ'          : params['safe_z'],
                'overlap'        : 0.5,
                'overlapFinish'  : 0.5,
                'maxCutDepth'    : params['roughing']['step_size'],
                'toolDiam'       : params['roughing']['diam_tool'],
                'direction'      : 'ccw',
                'startDwell'     : 1.0,
                }
        pocket = cnc_pocket.CircAnnulusPocketXY(annulus_params)
        prog.add(pocket)

        last_step_z = first_step_z

        for data in toolpath_annulus_data:

            thickness = min(max_radius, max_radius - (data['radius'] - 0.5*params['roughing']['diam_tool']))
            #print(thickness - params['roughing']['diam_tool'])
            if abs(thickness - params['roughing']['diam_tool']) < 1.0e-9:
                thickness = params['roughing']['diam_tool']
            annulus_params = { 
                    'centerX'        : pos['x'], 
                    'centerY'        : pos['y'],
                    'radius'         : max_radius,
                    'thickness'      : thickness,
                    'depth'          : abs(data['step_z']) - abs(last_step_z),
                    'startZ'         : last_step_z,
                    'safeZ'          : params['safe_z'],
                    'overlap'        : 0.5,
                    'overlapFinish'  : 0.5,
                    'maxCutDepth'    : params['roughing']['step_size'],
                    'toolDiam'       : params['roughing']['diam_tool'],
                    'direction'      : 'ccw',
                    'startDwell'     : 1.0,
                    }
            pocket = cnc_pocket.CircAnnulusPocketXY(annulus_params)
            prog.add(pocket)
            last_step_z = data['step_z']

    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.End(),comment=True)
    return prog



# Pocket array functions
# --------------------------------------------------------------------------------------------------

def max_margin(params):
    return max(params['roughing']['margin'], params['finishing']['margin'])

def max_diam_tool(params):
    return max(params['roughing']['diam_tool'], params['finishing']['diam_tool'])

def pocket_outer_diam(params):
    return params['diam_sphere'] + 2*max_margin(params) + 2*max_diam_tool(params)

def linear_positions(pocket_diam, num_pocket, bridge_width):
    pos_init =  2*bridge_width + 0.5*pocket_diam
    pos_list = [pos_init]
    for i in range(1,num_pocket):
        pos_list.append(pos_list[i-1] + pocket_diam + bridge_width)
    return pos_list

def pocket_centers(params):
    pocket_diam = pocket_outer_diam(params)
    pos_x = linear_positions(pocket_diam, params['num_x'], params['bridge_width'])
    pos_y = linear_positions(pocket_diam, params['num_y'], params['bridge_width'])
    pos_xy = [{'x': x, 'y': y} for x in pos_x for y in pos_y]
    return pos_xy

def material_rect(params):
    pos_xy = pocket_centers(params)
    pos_x = [p['x'] for p in pos_xy]
    pos_y = [p['y'] for p in pos_xy]
    pocket_diam = params['diam_sphere'] + 2*max_margin(params) + 2*max_diam_tool(params)
    delta = 2*params['bridge_width'] + 0.5*pocket_diam
    min_x = min(pos_x) - delta
    max_x = max(pos_x) + delta
    min_y = min(pos_y) - delta
    max_y = max(pos_y) + delta
    width = max_x - min_x
    height = max_y - min_y
    return {'x': min_x, 'y': min_y, 'w':  width, 'h': height}


# Plotting utilities
# -------------------------------------------------------------------------------------------------

def plot_material_boundary(params,color='r'):
    rect = material_rect(params)
    x0 = rect['x']
    x1 = rect['x'] + rect['w']
    xvals = [x0,x1,x1,x0,x0] 
    y0 = rect['y']
    y1 = rect['y'] + rect['h']
    yvals = [y0,y0,y1,y1,y0]
    plt.plot(xvals,yvals,color)

def plot_pocket_centers(params,color='b'):
    pos_list = pocket_centers(params)
    xvals = [p['x'] for p in pos_list]
    yvals = [p['y'] for p in pos_list]
    plt.plot(xvals,yvals,color+'o')

def plot_pocket_boundaries(params,color='g'): 
    diam = pocket_outer_diam(params)
    pos_list = pocket_centers(params)
    t =  np.linspace(0,1,500)
    circ_x = 0.5*diam*np.cos(2.0*np.pi*t)
    circ_y = 0.5*diam*np.sin(2.0*np.pi*t)
    for p in pos_list:
        plt.plot(circ_x + p['x'], circ_y + p['y'], color)

def plot_spheres(params,color='m'):
    diam = params['diam_sphere']
    pos_list = pocket_centers(params)
    t =  np.linspace(0,1,500)
    circ_x = 0.5*diam*np.cos(2.0*np.pi*t)
    circ_y = 0.5*diam*np.sin(2.0*np.pi*t)
    for p in pos_list:
        plt.plot(circ_x + p['x'], circ_y + p['y'], color)



# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    
    params = {
        'num_x'          : 3,
        'num_y'          : 5,
        'diam_sphere'    : mm_to_inch(12.0),
        'tab_thickness'  : 0.01,
        'bridge_width'   : 0.2,
        'center_z'       : -0.75/2.0,
        'safe_z'         : 0.5,
        'roughing' : {
            'diam_tool'  : 1.0/3.0,
            'margin'     : 0.01,
            'step_size'  : 0.1,
            },
        'finishing': {
            'diam_tool'  : 1.0/8.0,
            'margin'     : 0.0,
            'step_size'  : 0.01,
            },
        }

    if 0:
        plot_pocket_centers(params)
        plot_material_boundary(params)
        plot_pocket_boundaries(params)
        plot_spheres(params)
        plt.axis('equal')
        plt.show()

    prog = create_roughing_program(params)
    #print(prog)
    prog.write('test.ngc')



    

    


#prog = gcode_cmd.GCodeProg()
#prog.add(gcode_cmd.GenericStart())
#prog.add(gcode_cmd.Space())
#prog.add(gcode_cmd.FeedRate(100.0))
#
#param = { 
#        'centerX'        : 0.0, 
#        'centerY'        : 0.0,
#        'radius'         : 1.0,
#        'thickness'      : 0.4,
#        'depth'          : 0.4,
#        'startZ'         : 0.0,
#        'safeZ'          : 0.5,
#        'overlap'        : 0.5,
#        'overlapFinish'  : 0.5,
#        'maxCutDepth'    : 0.2,
#        'toolDiam'       : 0.125,
#        'direction'      : 'ccw',
#        'startDwell'     : 1.0,
#        }
#
#pocket = cnc_pocket.CircAnnulusPocketXY(param)
#
#prog.add(pocket)
#prog.add(gcode_cmd.Space())
#prog.add(gcode_cmd.End(),comment=True)
#print(prog)
#prog.write('test.ngc')
