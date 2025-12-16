import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.interpolate import interp1d

#%% ============================ MASW functions =============================================

# From  https://github.com/JoseCunhaTeixeira/PAC
def phase_shift(XT, si, offsets, vmin, vmax, dv, fmax, fmin=0):
    """
    Constructs a FV dispersion diagram with the phase-shift method from Park et al. (1999)
    args :
        XT (numpy array) : data
        si (float) : sampling interval in seconds
        offsets (numpy array) : offsets in meter
        vmin, vmax (float) : velocities to scan in m/s
        dv (float) : velocity step in m/s
        fmax (float) : maximum frequency computed
        fmin (float) : minimum frequency computed (default: 0)
    returns :
        fs : frequency axis
        vs : velocity axis
        FV: dispersion plot
    """   
    XT = np.array(XT)
    offsets = np.array(offsets)

    # Ensure offsets is at least 1D
    if offsets.ndim == 0:
        offsets = np.array([offsets])

    # Filtering dead traces
    non_zero_mask = ~np.all(XT == 0, axis=1)
    XT = XT[non_zero_mask]
    offsets = offsets[non_zero_mask]

    if XT.shape[0] == 0:
        raise ValueError("Dead traces detected.")
    
    # Ensure we have at least 2 traces for phase shift analysis
    if XT.shape[0] < 2:
        raise ValueError("Phase shift analysis requires at least 2 traces.")

    Nt = XT.shape[1]  
    XF = rfft(XT, axis=(1), n=Nt)  
    fs = rfftfreq(Nt, si)
    
    # print(f"Shapes: \n XT : {XT.shape} \n fs : {fs.shape} \n XF : {XF.shape}")
    
    if np.any(XT==0):
        zero_values=np.argwhere(XF == 0)
        # print(f"XT contains {len(zero_values)} zero at positions {zero_values}")
    
    if np.any(XF==0):
        zero_values=np.argwhere(XF == 0)
        # print(f"XF contains {len(zero_values)} zero at positions {zero_values}")
    
    # Find frequency range indices
    try:
        fimin = np.where(fs >= fmin)[0][0]
    except:
        fimin = 0
        
    try:
        fimax = np.where(fs >= fmax)[0][0]
    except:
        fimax = len(fs)-1
        
    # Extract frequency range
    fs = fs[fimin:fimax+1]
    XF = XF[:, fimin:fimax+1]
    
    vs = np.arange(vmin, vmax, dv)

    # Vecrorized version (otpimized)
    FV = np.zeros((len(fs), len(vs)))
    eps = 1e-12
    for v_i, v in enumerate(vs):
        # Ensure proper broadcasting - offsets should be (n_traces, 1) and fs should be (1, n_freqs)
        offsets_reshaped = offsets.reshape(-1, 1)  # (n_traces, 1)
        fs_reshaped = fs.reshape(1, -1)  # (1, n_freqs)

        dphi = 2 * np.pi * offsets_reshaped * fs_reshaped / v  # (n_traces, n_freqs)

        # Robust phase normalization: avoid divide-by-zero when |XF|==0
        abs_XF = np.abs(XF)
        phase_norm = np.divide(XF, abs_XF, out=np.zeros_like(XF, dtype=XF.dtype), where=abs_XF > eps)

        # XF is (n_traces, n_freqs), dphi is (n_traces, n_freqs)
        FV[:, v_i] = np.abs(np.sum(phase_norm * np.exp(1j * dphi), axis=0))


    return fs, vs, FV

### -----------------------------------------------------------------------------------------------
def resamp_wavelength(f, v):
    w = v / f
    func_v = interp1d(w, v)
    w_resamp = arange(np.ceil(min(w)), np.floor(max(w)), 1)
    v_resamp = func_v(w_resamp)
    return w_resamp, v_resamp[::-1]
### -----------------------------------------------------------------------------------------------


### -----------------------------------------------------------------------------------------------
def resamp_frequency(f, v):
    func_v = interp1d(f, v)
    f_resamp = arange(np.ceil(min(f)), np.floor(max(f)), 1)
    v_resamp = func_v(f_resamp)
    return f_resamp, v_resamp[::-1]
### -----------------------------------------------------------------------------------------------

### -----------------------------------------------------------------------------------------------
def resamp(f, v, err, wmax=None):
    w = v / f
    min_w = np.ceil(min(w))
    max_w = np.floor(max(w))
    if min_w < max_w:
        func_v = interp1d(w, v, kind='linear')
        func_err = interp1d(w, err, kind='linear', fill_value='extrapolate')
        w_resamp = arange(min_w, max_w, 1)
        v_resamp = func_v(w_resamp)
        err_resamp = func_err(w_resamp)
        if wmax is not None:
            if max(w_resamp) > wmax:
                try:
                    idx = np.where(w_resamp >= wmax)[0][0]
                except:
                    idx = len(w_resamp)-1
                w_resamp = w_resamp[:idx+1]
                v_resamp = v_resamp[:idx+1]
                err_resamp = err_resamp[:idx+1]
        f_resamp = v_resamp/w_resamp
        f_resamp, v_resamp, err_resamp = zip(*sorted(zip(f_resamp, v_resamp, err_resamp)))
    else : 
        f_resamp = [f[0]]
        v_resamp = [v[0]]
        err_resamp = [err[0]]
    return f_resamp, v_resamp, err_resamp
### -----------------------------------------------------------------------------------------------

### -----------------------------------------------------------------------------------------------
def lorentzian_error(v_picked, f_picked, dx, Nx, a=0.5):
    # Factor to adapt error depending on window size
    fac = 10**(1/np.sqrt(Nx*dx))
    
    # Resolution
    Dc_left = 1 / (1/v_picked - 1/(2*f_picked*Nx*fac*dx))
    Dc_right = 1 / (1/v_picked + 1/(2*f_picked*Nx*fac*dx))
    Dc = np.abs(Dc_left - Dc_right)
    
    # Absolute uncertainty
    dc = (10**-a) * Dc

    for i, (err, v) in enumerate(zip(dc, v_picked)):
        if err > 0.4*v :
            dc[i] = 0.4*v
        if err < 5 :
            dc[i] = 5

    return dc

### -----------------------------------------------------------------------------------------------
def arange(start, stop, step):
    """
    Mimics np.arange but ensures the stop value is included 
    when it should be, avoiding floating-point precision issues.
    """
    num_steps = int(round((stop - start) / step)) + 1  # Compute exact number of steps
    return np.linspace(start, stop, num_steps)
