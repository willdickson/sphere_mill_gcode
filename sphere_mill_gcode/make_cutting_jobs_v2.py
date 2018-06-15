import copy
import matplotlib.pyplot as plt
from utility import mm_to_inch
from sphere_array import *

params = {
    'num_x'          : 4,
    'num_y'          : 2,
    #'diam_sphere'    : mm_to_inch(12.0),
    'diam_sphere'    : mm_to_inch(10.0),
    'num_tab'        : 3,
    'tab_thickness'  : 0.06, # 0.02 too small (almost works), 0.08 too big
    'tab_width'      : 0.15,
    'bridge_width'   : 0.2,
    'boundary_pad'   : 0.6,
    'center_z'       : -1.0/2.0,
    'safe_z'         : 0.25,
    'start_dwell'    : 2.0,
    'stockcut': {
        'thickness'    : 1.0,
        'spacing_fact' : 1.25,
        'overcut'      : 0.05,
        'drill_inset'  : 0.40,
        'drill_step'   : 0.10,
        'raw_sheet_x'  : 24.0,  # raw sheet size
        'raw_sheet_y'  : 12.0,
        'cut_sheet_x'  : 6.25,  # cut sheet size
        'cut_sheet_y'  : 2.75,
        'feedrate'     : 100.0,
        'diam_tool'    : 3.0/8.0,
        'step_size'    : 0.15,
        },
    'jigcut': {
        'margin'    : 2.0,
        'depth'     : 0.15,
        'feedrate'  : 100.0,
        'diam_tool' : 1.5,
        'step_size' : 0.05,
        },
    'roughing' : {
        'feedrate'   : 60.0,
        'diam_tool'  : 1.0/4.0,
        'margin'     : 0.03,
        'step_size'  : 0.05,
        },
    'finishing': {
        'feedrate'   : 40.0,
        'diam_tool'  : 1.0/8.0,
        'margin'     : 0.0,
        'step_size'  : 0.01,
        },
    }

if 1:
    params_tmp = copy.deepcopy(params)
    params_tmp['stockcut']['thickness'] = 0.15
    stockcut_shallow = create_stockcut_program(params_tmp)
    stockcut_shallow.write('stockcut_shallow.ngc')

if 1:
    stockdrill = create_stockcut_drill(params)
    stockdrill.write('stockcut_drill.ngc')

if 1:
    stockcut = create_stockcut_program(params)
    stockcut.write('stockcut.ngc')

if 1:
    jigcut = create_jigcut_program(params)
    jigcut.write('jigcut.ngc')

if 1:
    align_drill = create_alignment_drill(params)
    align_drill.write('align_drill.ngc')

if 1:
    params_tmp = copy.deepcopy(params)
    params_tmp['tab_thickness'] = 0.0
    roughing = create_roughing_program(params_tmp)
    roughing.write('roughing_0.ngc')

    roughing = create_roughing_program(params)
    roughing.write('roughing_1.ngc')

if 1:
    params_tmp = copy.deepcopy(params)
    params_tmp['tab_thickness'] = 0.0
    finishing = create_finishing_program(params_tmp)
    finishing.write('finishing_0.ngc')

    finishing = create_finishing_program(params)
    finishing.write('finishing_1.ngc')

if 1:
    tabcut = create_tabcut_program(params,contour=True)
    tabcut.write('tabcut.ngc')

if 1:
    pos_nums = [5,6]
    tabcut = create_tabcut_program(params,remove=True,contour=True,pos_nums=pos_nums)
    tabcut.write('tabremove.ngc')

if 0:
    plot_sphere_array(params,fignum=1)
    plot_stockcut(params,fignum=2)
    plot_finishing_toolpos(params,fignum=3)
    plot_roughing_toolpos(params,fignum=4)
    plt.show()
