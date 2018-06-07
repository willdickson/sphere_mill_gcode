from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
import py2gcode.gcode_cmd as gcode_cmd
import py2gcode.cnc_path as cnc_path
import py2gcode.cnc_pocket as cnc_pocket
import py2gcode.cnc_boundary as cnc_boundary
import py2gcode.cnc_drill as cnc_drill

import flat_endmill
import ball_endmill
import ball_endmill_viz 
import flat_endmill_viz

from finishing_routine import SphereFinishingRoutine
from arc_routine import ArcRoutine

def create_jigcut_program(params):

    prog = gcode_cmd.GCodeProg()
    prog.add(gcode_cmd.GenericStart())
    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.FeedRate(params['stockcut']['feedrate']))

    margin = params['jigcut']['margin']
    depth = params['jigcut']['depth']
    safe_z = params['safe_z']
    step_size = params['jigcut']['step_size']
    diam_tool = params['jigcut']['diam_tool']
    start_dwell = params['start_dwell']
    dx = params['stockcut']['cut_sheet_x'] + margin
    dy = params['stockcut']['cut_sheet_y'] + margin

    cx = 0.5*dx
    cy = 0.5*dy

    param = {
            'centerX'       : cx,
            'centerY'       : cy,
            'width'         : dx,
            'height'        : dy,
            'depth'         : depth,
            'startZ'        : 0.0,
            'safeZ'         : safe_z,
            'overlap'       : 0.5,
            'overlapFinish' : 0.5,
            'maxCutDepth'   : step_size,
            'toolDiam'      : diam_tool,
            'cornerCut'     : True,
            'direction'     : 'ccw',
            'startDwell'    : start_dwell,
            }
    pocket = cnc_pocket.RectPocketXY(param)
    prog.add(pocket)

    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.End(),comment=True)
    return prog


def create_stockcut_drill(params):
    prog = gcode_cmd.GCodeProg()
    prog.add(gcode_cmd.GenericStart())
    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.FeedRate(params['stockcut']['feedrate']))

    thickness = params['stockcut']['thickness']
    overcut = params['stockcut']['overcut']
    diam_tool = params['stockcut']['diam_tool']
    step_size = params['stockcut']['step_size']
    start_dwell = params['start_dwell']
    drill_step = params['stockcut']['drill_step']
    drill_inset = params['stockcut']['drill_inset']
    start_z = 0.0 
    safe_z = params['safe_z']

    pocket_data = get_stockcut_pocket_data(params)
    
    for data in pocket_data:
        for i in (-1,1):
            for j in (-1,1):
                cx = data['x'] + 0.5*data['w'] + i*(0.5*data['w'] - drill_inset)
                cy = data['y'] + 0.5*data['h'] + j*(0.5*data['h'] - drill_inset)

                param = {
                        'centerX'      : cx, 
                        'centerY'      : cy, 
                        'startZ'       : start_z,
                        'stopZ'        : start_z - (thickness + overcut),
                        'safeZ'        : safe_z,
                        'stepZ'        : drill_step,
                        'startDwell'   : start_dwell,
                        }

                drill = cnc_drill.PeckDrill(param)
                prog.add(drill)

    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.End(),comment=True)
    return prog


def create_stockcut_program(params):

    prog = gcode_cmd.GCodeProg()
    prog.add(gcode_cmd.GenericStart())
    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.FeedRate(params['stockcut']['feedrate']))

    thickness = params['stockcut']['thickness']
    overcut = params['stockcut']['overcut']
    diam_tool = params['stockcut']['diam_tool']
    step_size = params['stockcut']['step_size']
    start_dwell = params['start_dwell']
    start_z = 0.0 
    safe_z = params['safe_z']

    pocket_data = get_stockcut_pocket_data(params)

    for data in pocket_data:
        param = { 
                'centerX'      : data['x'] + 0.5*data['w'],
                'centerY'      : data['y'] + 0.5*data['h'],
                'width'        : data['w'],
                'height'       : data['h'],
                'depth'        : thickness + overcut,
                'radius'       : None,
                'startZ'       : start_z,
                'safeZ'        : safe_z,
                'toolDiam'     : diam_tool,
                'cutterComp'   : 'outside',
                'direction'    : 'ccw',
                'maxCutDepth'  : step_size,
                'startDwell'   : start_dwell,
                }
        boundary = cnc_boundary.RectBoundaryXY(param)
        prog.add(boundary)

    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.End(),comment=True)
    return prog


def get_stockcut_pocket_data(params):
    raw_sheet_x = params['stockcut']['raw_sheet_x']
    raw_sheet_y = params['stockcut']['raw_sheet_y']
    cut_sheet_x = params['stockcut']['cut_sheet_x']
    cut_sheet_y = params['stockcut']['cut_sheet_y']
    tool_diam = params['stockcut']['diam_tool']
    spacing_fact = params['stockcut']['spacing_fact']

    hole_dx = cut_sheet_x +  2*spacing_fact*tool_diam
    hole_dy = cut_sheet_y +  2*spacing_fact*tool_diam

    num_x = int(np.floor(raw_sheet_x/hole_dx))
    num_y = int(np.floor(raw_sheet_y/hole_dy))

    start_x = 0.5*raw_sheet_x - 0.5*num_x*hole_dx
    start_y = 0.5*raw_sheet_y - 0.5*num_y*hole_dy

    pocket_data = []
    for i in range(num_x):
        for j in range(num_y):
            cx = start_x + i*hole_dx + spacing_fact*tool_diam 
            cy = start_y + j*hole_dy + spacing_fact*tool_diam
            pocket_data.append({ 'x': cx, 'y': cy, 'w': cut_sheet_x, 'h': cut_sheet_y })
    return pocket_data



def create_finishing_program(params):

    prog = gcode_cmd.GCodeProg()
    prog.add(gcode_cmd.GenericStart())
    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.FeedRate(params['finishing']['feedrate']))

    pos_list = pocket_centers(params)
    toolpath_params = { 
            'diam_sphere'   : params['diam_sphere'],
            'diam_tool'     : params['finishing']['diam_tool'],
            'margin'        : params['finishing']['margin'],
            'step_size'     : params['finishing']['step_size'],
            'tab_thickness' : params['tab_thickness'],
            'center_z'      : params['center_z'],
            }
    toolpath_annulus_data = ball_endmill.get_toolpath_annulus_data(toolpath_params)

    for pos in pos_list:
        start_z  = toolpath_annulus_data[0]['step_z'] + params['roughing']['margin']
        routine_params = { 
                'centerX'        : pos['x'],
                'centerY'        : pos['y'],
                'startZ'         : start_z,
                'safeZ'          : params['safe_z'],
                'startDwell'     : params['start_dwell'],
                'toolpathData'   : toolpath_annulus_data,
                'direction'      : 'ccw',
                }
        routine = SphereFinishingRoutine(routine_params)
        prog.add(routine)

    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.End(),comment=True)
    return prog


def create_roughing_program(params):

    prog = gcode_cmd.GCodeProg()
    prog.add(gcode_cmd.GenericStart())
    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.FeedRate(params['roughing']['feedrate']))

    pos_list = pocket_centers(params)
    toolpath_params = { 
            'diam_sphere'   : params['diam_sphere'],
            'diam_tool'     : params['roughing']['diam_tool'],
            'margin'        : params['roughing']['margin'],
            'step_size'     : params['roughing']['step_size'],
            'tab_thickness' : params['tab_thickness'],
            'center_z'      : params['center_z'],
            }
    toolpath_annulus_data = flat_endmill.get_toolpath_annulus_data(toolpath_params)

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
                'startDwell'     : params['start_dwell'],
                }
        pocket = cnc_pocket.CircAnnulusPocketXY(annulus_params)
        prog.add(pocket)

        # Rough out half sphere pocket
        last_step_z = first_step_z
        for data in toolpath_annulus_data:

            thickness = min(max_radius, max_radius - (data['radius'] - 0.5*params['roughing']['diam_tool']))
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
                    'startDwell'     : params['start_dwell'],
                    }
            pocket = cnc_pocket.CircAnnulusPocketXY(annulus_params)
            prog.add(pocket)
            last_step_z = data['step_z']

        # Final cut at sphere boundary to remove chamfer
        thickness = params['roughing']['diam_tool']
        radius = 0.5*params['diam_sphere'] + thickness
        start_z = toolpath_annulus_data[-2]['step_z']
        stop_z = toolpath_annulus_data[-1]['step_z']
        annulus_params = { 
                'centerX'        : pos['x'], 
                'centerY'        : pos['y'],
                'radius'         : radius,
                'thickness'      : thickness,
                'depth'          : abs(stop_z - start_z),
                'startZ'         : start_z,
                'safeZ'          : params['safe_z'],
                'overlap'        : 0.5,
                'overlapFinish'  : 0.5,
                'maxCutDepth'    : params['roughing']['step_size'],
                'toolDiam'       : params['roughing']['diam_tool'],
                'direction'      : 'ccw',
                'startDwell'     : params['start_dwell'],
                }
        pocket = cnc_pocket.CircAnnulusPocketXY(annulus_params)
        prog.add(pocket)

    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.End(),comment=True)
    return prog


def get_tabcut_data(params,remove=False,pos_nums=None):
    diam_sphere = params['diam_sphere']
    diam_tool = params['finishing']['diam_tool']

    num_tab = params['num_tab']
    tab_thickness = params['tab_thickness']
    tab_width = params['tab_width']

    pos_list = pocket_centers(params)
    toolpath_params = { 
            'diam_sphere'   : params['diam_sphere'],
            'diam_tool'     : params['finishing']['diam_tool'],
            'margin'        : params['finishing']['margin'],
            'step_size'     : params['finishing']['step_size'],
            'tab_thickness' : params['tab_thickness'],
            'center_z'      : params['center_z'],
            }
    toolpath_annulus_data = flat_endmill.get_toolpath_annulus_data(toolpath_params)

    radius = 0.5*diam_sphere + 0.5*diam_tool
    last_step_z = toolpath_annulus_data[-1]['step_z']
    depth = params['tab_thickness'] + min([1.25*diam_tool,0.25*diam_sphere])

    # Get arc requied for tab cuts
    circumference = 2.0*np.pi*radius
    total_tab_arc = num_tab*tab_width
    total_cut_arc = circumference - total_tab_arc - num_tab*diam_tool
    cut_arc = total_cut_arc/num_tab
    cut_ang_rad = cut_arc/radius
    cut_ang_deg = np.rad2deg(cut_ang_rad)

    # Get angles for tab cuts
    ang_step_deg = 360.0/float(num_tab)
    ang_neg_list = [(-0.5*cut_ang_deg + ang_step_deg*i) for i in range(num_tab)] 
    ang_pos_list = [( 0.5*cut_ang_deg + ang_step_deg*i) for i in range(num_tab)] 
    if not remove:
        ang_list = [(x,y) for x, y in zip(ang_neg_list, ang_pos_list)]
    else:
        ang_neg_list.append(ang_neg_list[0])
        ang_neg_list = ang_neg_list[1:]
        ang_list = [(x,y) for x, y in zip(ang_pos_list, ang_neg_list)]

    tabcut_data = []
    for i,pos in enumerate(pos_list):
        center = (pos['x'], pos['y'])
        if (pos_nums is not None) and (i not in pos_nums):
            continue
        for ang in ang_list:
            tabcut_data.append({
                'x'        : pos['x'], 
                'y'        : pos['y'], 
                'start_z'  : last_step_z,
                'depth'    : depth, 
                'radius'   : radius,
                'angles'   : ang, 
                })
    return tabcut_data


def create_tabcut_program(params,remove=False, pos_nums=None):

    prog = gcode_cmd.GCodeProg()
    prog.add(gcode_cmd.GenericStart())
    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.FeedRate(params['finishing']['feedrate']))

    safe_z = params['safe_z']

    tabcut_data = get_tabcut_data(params,remove=remove,pos_nums=pos_nums)

    for data in tabcut_data:
        tabcut_params = { 
                'centerX'        : data['x'], 
                'centerY'        : data['y'],
                'radius'         : data['radius'],
                'depth'          : data['depth'],
                'startZ'         : data['start_z'],
                'angles'         : data['angles'],
                'safeZ'          : params['safe_z'],
                'maxCutDepth'    : params['finishing']['step_size'],
                'toolDiam'       : params['finishing']['diam_tool'],
                'startDwell'     : params['start_dwell'],
                }
        arc = ArcRoutine(tabcut_params)
        prog.add(arc)

    prog.add(gcode_cmd.Space())
    prog.add(gcode_cmd.End(),comment=True)
    return prog


def get_tab_remove_data(params):
    tabcut_data = get_tabcut_data(params, remove=True)

    for data in tabcut_data:
        pass

# Pocket array functions
# --------------------------------------------------------------------------------------------------

def max_margin(params):
    return max(params['roughing']['margin'], params['finishing']['margin'])


def max_diam_tool(params):
    return max(params['roughing']['diam_tool'], params['finishing']['diam_tool'])


def pocket_outer_diam(params):
    return params['diam_sphere'] + 2*max_margin(params) + 2*max_diam_tool(params)


def linear_positions(pocket_diam, num_pocket, bridge_width):
    pos_init = 0.0
    pos_list = [pos_init]
    for i in range(1,num_pocket):
        pos_list.append(pos_list[i-1] + pocket_diam + bridge_width)
    return pos_list


def pocket_centers(params):
    pocket_diam = pocket_outer_diam(params)
    pos_x = linear_positions(pocket_diam, params['num_x'], params['bridge_width'])
    pos_y = linear_positions(pocket_diam, params['num_y'], params['bridge_width'])
    delta_x = max(pos_x) - min(pos_x)
    delta_y = max(pos_y) - min(pos_y)
    stock_x = params['stockcut']['cut_sheet_x']
    stock_y = params['stockcut']['cut_sheet_y']
    #pos_xy = [{'x': x + 0.5*stock_x - 0.5*delta_x, 'y': y + 0.5*stock_y -0.5*delta_y} for x in pos_x for y in pos_y]
    pos_xy = [{'x': x - 0.5*delta_x, 'y': y - 0.5*delta_y} for x in pos_x for y in pos_y]
    return pos_xy


def material_rect(params):
    #min_x = 0.0
    #min_y = 0.0
    min_x = -0.5*params['stockcut']['cut_sheet_x']
    min_y = -0.5*params['stockcut']['cut_sheet_y']
    width = params['stockcut']['cut_sheet_x']
    height = params['stockcut']['cut_sheet_y']
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


def plot_tabcut(params,color='y'):
    tabcut_data = get_tabcut_data(params)
    diam_tool = params['finishing']['diam_tool']

    for data in tabcut_data:

        radius_mid = data['radius']
        radius_inner = radius_mid - 0.5*diam_tool
        radius_outer = radius_mid + 0.5*diam_tool

        ang0, ang1 = map(np.deg2rad, data['angles'])
        t_arc = np.linspace(ang0,ang1)
        cx_arc = data['x']
        cy_arc = data['y']

        for radius in (radius_inner, radius_outer):
            x_arc = cx_arc + radius*np.cos(t_arc)
            y_arc = cy_arc + radius*np.sin(t_arc)
            plt.plot(x_arc,y_arc,color)

        t_end = np.linspace(0,2.0*np.pi)
        for ang in (ang0,ang1):
            cx_end = cx_arc + radius_mid*np.cos(ang)
            cy_end = cy_arc + radius_mid*np.sin(ang)
            x_end = cx_end + 0.5*diam_tool*np.cos(t_end)
            y_end = cy_end + 0.5*diam_tool*np.sin(t_end)
            plt.plot(x_end, y_end, color)



def plot_sphere_array(params, fignum=1): 
    plt.figure(fignum)
    plot_pocket_centers(params)
    plot_material_boundary(params)
    plot_pocket_boundaries(params)
    plot_spheres(params)
    plot_tabcut(params)
    plt.plot([0],[0],'+k')
    plt.title('sphere array')
    plt.xlabel('x (in)')
    plt.ylabel('y (in)')
    plt.axis('equal')



def plot_raw_sheet(params,color='k'):
    x0 = 0.0
    y0 = 0.0
    x1 = params['stockcut']['raw_sheet_x']
    y1 = params['stockcut']['raw_sheet_y']
    plt.plot([x0,x1,x1,x0,x0],[y0,y0,y1,y1,y0],color)


def plot_stockcut(params,fignum=2):
    pocket_data = get_stockcut_pocket_data(params)
    plt.figure(fignum)
    plot_raw_sheet(params)
    for data in pocket_data:
        x0 = data['x']
        y0 = data['y']
        x1 = x0 + data['w']
        y1 = y0 + data['h']
        plt.plot([x0,x1,x1,x0,x0],[y0,y0,y1,y1,y0],'b')
    plt.axis('equal')
    plt.xlabel('x')
    plt.ylabel('u')
    plt.title('stockcut')


def plot_finishing_toolpos(params,fignum=3):
    plot_params = { 
            'diam_sphere'   : params['diam_sphere'],
            'diam_tool'     : params['finishing']['diam_tool'],
            'margin'        : params['finishing']['margin'],
            'step_size'     : params['finishing']['step_size'],
            'tab_thickness' : params['tab_thickness'],
            'center_z'      : params['center_z'],
            }
    plt.figure(fignum)
    ball_endmill_viz.plot_spheremill_toolpos(plot_params) 
    plt.axis('equal')
    plt.grid('on')


def plot_roughing_toolpos(params,fignum=4):
    plot_params = { 
            'diam_sphere'   : params['diam_sphere'],
            'diam_tool'     : params['roughing']['diam_tool'],
            'margin'        : params['roughing']['margin'],
            'step_size'     : params['roughing']['step_size'],
            'tab_thickness' : params['tab_thickness'],
            'center_z'      : params['center_z'],
            }
    plt.figure(fignum)
    flat_endmill_viz.plot_spheremill_toolpos(plot_params)
    plt.axis('equal')
    plt.grid('on')
    plt.show()




