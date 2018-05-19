import numpy as np
import matplotlib.pyplot as plt


def angle_to_step(angle,diam_sphere):
    """
    Returns the step down for a given angle. 

    Notes:  
    * the top of the sphere (assumed to be at z=0) 
    * the angle should be in range (0,pi/2) where 0 is the top of the sphere. 
    """
    return 0.5*diam_sphere*(1.0 - np.cos(angle))


def step_to_angle(step,diam_sphere):
    """
    Returns the angle on the sphere for a given step down.
    """
    return np.arccos(1 - step/(0.5*diam_sphere))


def get_equal_angle_steps(diam_sphere, tab_thickness, num_steps, margin):
    """
    Computes the vertical (z) steps (z) required to go from the top of the top
    of a sphere to mid-sphere + 0.5*tab_thickness in equal angle steps sizes
    (measured from the center of the sphere) using an endmill.
    """
    diam_effective = diam_sphere + 2*margin
    abs_step_min = 0.0 
    abs_step_max = 0.5*diam_effective - 0.5*tab_thickness
    angle_min = step_to_angle(abs_step_min, diam_effective)
    angle_max = step_to_angle(abs_step_max, diam_effective)
    angle_array = np.linspace(angle_min, angle_max,num_steps)
    abs_step_array = angle_to_step(angle_array, diam_effective)
    step_array = -1.0*abs_step_array + margin
    return step_array

def get_num_steps(diam_sphere, tab_thickness, step_size, margin):
    diam_effective = diam_sphere + 2*margin
    num_steps = int(np.ceil(0.5*(diam_effective - tab_thickness)/step_size))
    return num_steps


def plot_circle(cx,cy,radius,color='r',num_pts=500):
    t = np.linspace(0.0,1.0,num_pts)
    x = radius*np.cos(2.0*np.pi*t) + cx
    y = radius*np.sin(2.0*np.pi*t) + cy
    plt.plot(x,y,color=color)


def unit_vector((x,y)):
    vec_len = np.sqrt(x**2 + y**2)
    return x/vec_len, y/vec_len


def mm_to_inch(val):
    return val/25.4


def inch_to_mm(val):
    return val*25.4
