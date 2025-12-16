"""
Inversion Manager Module for Pyckster

This module handles seismic traveltime inversion processes, including data preparation,
inversion setup, and execution.
"""

import os
import numpy as np
from pygimli.physics import TravelTimeManager as refrac

def run_inversion_from_file(sgt_file, params=None):
    """
    Run seismic traveltime inversion from a .sgt file.
    
    Parameters:
    -----------
    sgt_file : str
        Path to the .sgt file containing picks data
    params : dict, optional
        Dictionary containing inversion parameters
    
    Returns:
    --------
    refrac_manager : TravelTimeManager
        PyGIMLI's TravelTimeManager object with inversion results
    """

    # Check if the file exists
    if not os.path.exists(sgt_file):
        print(f"Error: File {sgt_file} does not exist.")
        return None
    
    # Create refraction manager from file
    try:
        refrac_manager = refrac(sgt_file)
    except Exception as e:
        print(f"Error creating refraction manager: {e}")
        return None
    
    return run_inversion(refrac_manager, params)

def run_inversion_from_manager(refrac_manager, params=None):
    """
    Run seismic traveltime inversion from a TravelTimeManager object.

    Parameters:
    -----------
    refrac_manager : TravelTimeManager
        PyGIMLI's TravelTimeManager object with picks data
    params : dict, optional
        Dictionary containing inversion parameters

    Returns:
    --------
    refrac_manager : TravelTimeManager
        PyGIMLI's TravelTimeManager object with inversion results
    """
    if not isinstance(refrac_manager, refrac):
        raise TypeError("refrac_manager must be an instance of TravelTimeManager")
    
    return run_inversion(refrac_manager, params)

def run_inversion(refrac_manager, params=None):
    """ Run seismic traveltime inversion on a TravelTimeManager object.
    This function prepares the inversion parameters, checks for negative times,
    and runs the inversion process.
    Parameters:
    -----------
    refrac_manager : TravelTimeManager
        PyGIMLI's TravelTimeManager object with picks data
    params : dict, optional
        Dictionary containing inversion parameters. If None, default parameters are used.
    Returns:
    --------
    refrac_manager : TravelTimeManager
        PyGIMLI's TravelTimeManager object with inversion results
    """
    
    # Initialize parameters dictionary if not provided
    if params is None:
        params = {}
    
    # Check for negative times and correct if necessary
    if np.any(refrac_manager.data['t'] < 0):
        correct_time_picks(refrac_manager, params.get('min_velocity', 500))
    
    # Create inversion parameter dictionary with defaults
    inversion_params = {
        'verbose': params.get('verbose', True),
        'vTop': params.get('vTop', 500),
        'vBottom': params.get('vBottom', 5000),
        'secNodes': params.get('secNodes', 2),
        'lam': params.get('lam', 30),
        'maxIter': params.get('maxIter', 6),
        'zWeight': params.get('zWeight', 0.5),
        'balanceDepth': params.get('balanceDepth', False),
    }
    
    # Add optional parameters only if they're not None
    optional_params = ['paraDX', 'paraDepth', 'paraMaxCellSize']
    for param in optional_params:
        if params.get(param) is not None:
            inversion_params[param] = params.get(param)
    
    # Run the inversion
    refrac_manager.invert(**inversion_params)
    
    # Print inversion QC
    print("chi2 =", round(refrac_manager.inv.chi2(), 2), 
          "- rrms =", round(refrac_manager.inv.relrms(), 2), '%')
    
    return refrac_manager

# Keep the existing correct_negative_times function unchanged
def correct_time_picks(refrac_manager, min_velocity=500):
    """
    Correct negative times in the picks, assuming a surface velocity.
    The function resets minimum times for each shot at 0, then corrects 
    the time picks with the minimum offset and the assumed surface velocity.
    
    Parameters:
    -----------
    refrac_manager : TravelTimeManager
        PyGIMLI's TravelTimeManager object with data
    min_velocity : float or array
        Minimum velocity for time correction in m/s
    """
    offset_max = None
    apply_positive_correction = True

    unique_sources = np.unique(refrac_manager.data['s'])
    sensor_positions = refrac_manager.data.sensors().array()
    
    if not isinstance(min_velocity, np.ndarray):
        min_velocity = np.ones(len(unique_sources)) * min_velocity

    no_correc = 0
    tneg_correc = 0
    tneg_offset_correc = 0
    tpos_correc = 0
    tpos_offset_correc = 0
    
    t_pick_original = np.copy(refrac_manager.data['t'])
    t_pick_corrected_all = np.array([])

    for i in range(len(unique_sources)):
        x_source = sensor_positions[unique_sources[i], 0]
        geophones = refrac_manager.data['g'][refrac_manager.data['s'] == unique_sources[i]]
        x_pick = sensor_positions[geophones, 0]
        t_pick = refrac_manager.data['t'][refrac_manager.data['s'] == unique_sources[i]]
        offset = np.abs(x_pick - x_source)
        min_picked_offset = np.min(offset)
        min_picked_time = np.min(t_pick)
        t_offset = np.min(offset) / min_velocity[i]

        if offset_max is None:
            max_picked_offset = np.max(offset)
        else:
            max_picked_offset = offset_max
            
        # Correct negative and 0 time picks
        if min_picked_time <= 0:
            t_pick_corr = t_pick - min_picked_time
            
            # Correct time picks when closest picked geophone is not at the source location
            if min_picked_offset > 0:
                t_pick_corrected = t_pick_corr + t_offset
                tneg_offset_correc += 1
            # No further correction if closest geophone is at the source location
            else:
                t_pick_corrected = t_pick_corr
                tneg_correc += 1
        # Correct positive time picks
        else:
            if apply_positive_correction:
                if min_picked_offset == 0:
                    # Correct positive time picks when closest picked geophone is at the source location
                    if min_picked_time > 0:
                        t_pick_corrected = t_pick - min_picked_time
                        tpos_correc += 1
                    else:
                        t_pick_corrected = t_pick
                        no_correc += 1
                # Correct positive time picks when closest picked geophone is within offset range
                elif min_picked_offset > 0 and min_picked_offset <= max_picked_offset:
                    t_pick_corrected = t_pick + (t_offset - min_picked_time)
                    tpos_offset_correc += 1
                else:
                    t_pick_corrected = t_pick
                    no_correc += 1
            else:
                t_pick_corrected = t_pick
                no_correc += 1

        t_pick_corrected_all = np.concatenate((t_pick_corrected_all, t_pick_corrected))

    # Update the data in the refraction manager
    for i in range(len(t_pick_corrected_all)):
        refrac_manager.data['t'][i] = t_pick_corrected_all[i]
        
    print(f"Time correction summary:")
    print(f"  No correction: {no_correc}")
    print(f"  Negative time correction: {tneg_correc}")
    print(f"  Negative time with offset correction: {tneg_offset_correc}")
    print(f"  Positive time correction: {tpos_correc}")
    print(f"  Positive time with offset correction: {tpos_offset_correc}")
    
def get_surf_velocity(refrac_manager, smooth=True, w=9, 
                      method='convolve',s=50, show_plot=False):

    sensor_positions = refrac_manager.data.sensors().array()
    unique_sources = np.unique(refrac_manager.data['s'])
    x_source_all = sensor_positions[unique_sources,0]
    
    x_surf_array = []
    vel_surf_array = []
    min_offset_array = []
    max_offset_array = []

    for i in range(len(unique_sources)):

        source_index = unique_sources[i]
        x_source = sensor_positions[source_index,0]
        geophone_index = refrac_manager.data['g'][refrac_manager.data['s']==source_index]
        x_pick = sensor_positions[geophone_index,0]
        t_pick = refrac_manager.data['t'][refrac_manager.data['s']==source_index]
        offset = np.round(x_pick - x_source,3)

        # plt.plot(x_source,0,'r*')
        # plt.plot(x_pick,t_pick,'b+')

        offset_left = offset[offset<0]
        offset_right = offset[offset>0]
        offset_zero = offset[offset==0]

        left_ok = False
        right_ok = False
        vel_left = []
        vel_right = []
        min_offset_left = []
        max_offset_left = []
        min_offset_right = []
        max_offset_right = []

        if len(offset_zero)>0: # If closest geophone is at the source location
            closest_geophone_left_index = geophone_index[np.where(offset==np.sort(offset_zero)[0])]
            closest_geophone_right_index = geophone_index[np.where(offset==np.sort(offset_zero)[0])]

            if len(offset_left)>0:
                second_geophone_left_index = geophone_index[np.where(offset==np.max(offset_left))]
                left_ok = True
                # print(offset_left)
                min_offset_left.append(0)
                max_offset_left.append(np.abs(np.sort(offset_left)[-1]))
            else:
                second_geophone_left_index = []
            
            if len(offset_right)>0:
                second_geophone_right_index = geophone_index[np.where(offset==np.min(offset_right))]
                right_ok = True
                # print(offset_right)
                min_offset_right.append(0)
                max_offset_right.append(np.abs(np.sort(offset_right)[0]))
            else:  
                second_geophone_right_index = []
                
        else: # If closest geophone is not at the source location
            if len(offset_left)>1:
                closest_geophone_left_index = geophone_index[np.where(offset==np.sort(offset_left)[-1])]
                second_geophone_left_index = geophone_index[np.where(offset==np.sort(offset_left)[-2])]
                left_ok = True
                min_offset_left.append(np.abs(np.sort(offset_left)[-1]))
                max_offset_left.append(np.abs(np.sort(offset_left)[-2]))

            else:
                closest_geophone_left_index = []
                second_geophone_left_index = []
            
            if len(offset_right)>1:
                closest_geophone_right_index = geophone_index[np.where(offset==np.sort(offset_right)[0])]
                second_geophone_right_index = geophone_index[np.where(offset==np.sort(offset_right)[1])]
                right_ok = True
                min_offset_right.append(np.abs(np.sort(offset_right)[0]))
                max_offset_right.append(np.abs(np.sort(offset_right)[1]))

            else:  
                closest_geophone_right_index = []
                second_geophone_right_index = []

        if left_ok:
            x1 = sensor_positions[closest_geophone_left_index,0]
            x2 = sensor_positions[second_geophone_left_index,0]
            indices = np.where(np.isin(geophone_index, closest_geophone_left_index))
            indices_list_closest = indices[0].tolist()
            y1 = np.max(t_pick[indices_list_closest])
            indices = np.where(np.isin(geophone_index, second_geophone_left_index))
            indices_list_second = indices[0].tolist()
            y2 = np.max(t_pick[indices_list_second])

            if y2 == y1:
                left_ok = False
            else:
                vel_left = np.abs((x2-x1)/(y2-y1))

            # plt.plot(sensor_positions[closest_geophone_left_index,0],t_pick[indices_list_closest],'g+')
            # plt.plot(sensor_positions[second_geophone_left_index,0],t_pick[indices_list_second],'g+')
                
        if right_ok:
            x1 = sensor_positions[closest_geophone_right_index,0]
            x2 = sensor_positions[second_geophone_right_index,0]
            indices = np.where(np.isin(geophone_index, closest_geophone_right_index))
            indices_list_closest = indices[0].tolist()
            y1 = np.max(t_pick[indices_list_closest])
            indices = np.where(np.isin(geophone_index, second_geophone_right_index))
            indices_list_second = indices[0].tolist()
            y2 = np.max(t_pick[indices_list_second])

            if y2 == y1:
                right_ok = False
            else:
                vel_right = np.abs((x2-x1)/(y2-y1))

            # plt.plot(sensor_positions[closest_geophone_right_index,0],t_pick[indices_list_closest],'y+')
            # plt.plot(sensor_positions[second_geophone_right_index,0],t_pick[indices_list_second],'y+')

        if left_ok and right_ok:
            vel = np.mean([vel_left,vel_right])
            min_offset = np.mean([min_offset_left,min_offset_right])
            max_offset = np.mean([max_offset_left,max_offset_right])
        elif left_ok:
            vel = vel_left[0]
            min_offset = min_offset_left[0]
            max_offset = max_offset_left[0]
        elif right_ok:
            vel = vel_right[0]
            min_offset = min_offset_right[0]
            max_offset = max_offset_right[0]

        x_surf_array.append(x_source)
        vel_surf_array.append(vel)
        min_offset_array.append(min_offset)
        max_offset_array.append(max_offset)

        # if left_ok:
        #     plt.plot((x_source+offset_left),(offset_left)/(-vel))
        # if right_ok:
        #     plt.plot((x_source+offset_right),(offset_right)/vel)

    # plt.show()

    if smooth:
        smooth_vel_surf_array = smooth_interpolation(x_source_all,x_surf_array,vel_surf_array,
                                                 size=w,method=method,s=s)
    else:
        smooth_vel_surf_array = vel_surf_array
    
    if show_plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(x_surf_array,vel_surf_array,'k')
        ax.plot(x_source_all,smooth_vel_surf_array,'b')
        ax.set_xlabel('X source (m)')
        ax.set_ylabel('Surface velocity (m/s)')
        plt.show()

    return np.column_stack((x_surf_array, smooth_vel_surf_array, 
                            vel_surf_array, min_offset_array, max_offset_array))

def spline_interp(x_interp,x,y,s=1):
    from scipy.interpolate import UnivariateSpline
    spline = UnivariateSpline(x, y, s=s)
    return spline(x_interp)

def median_filter(x, size):
    '''Median filter of x with window w.'''
    from scipy.ndimage import median_filter
    return median_filter(x,size=size)

def moving_average(x, size=5, method='convolve'):
    '''Moving average of x with window size. Method can be 'convolve' or 'sagvol'''
    from scipy.signal import savgol_filter
    from scipy.ndimage import uniform_filter1d

    if method == 'convolve':
        return uniform_filter1d(x,size=size)
    elif method == 'sagvol':
        return savgol_filter(x, size, 2)

def smooth_interpolation(x_interp,x,y,size=9,method='convolve',s=None):
    '''Smooth interpolation of x and y with window size. Method can be 'convolve' or 'sagvol'''
    y_interp = spline_interp(x_interp,x,y,s=s)
    y_interp = median_filter(y_interp,size)
    y_interp = moving_average(y_interp,size,method=method)
    return y_interp