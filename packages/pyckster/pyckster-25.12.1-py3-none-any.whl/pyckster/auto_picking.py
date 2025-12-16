import numpy as np
from scipy import signal, stats
import matplotlib.pyplot as plt
from obspy import Stream, Trace

from .obspy_utils import read_seismic_file

def mnw_picker(trace, Td, beta=0.005):
    """
    Implements the Multi-Nested Windows (MNW) method to detect first arrivals.

    Args:
        trace (obspy.Trace): Seismic trace.
        Td (float): Dominant period of the P-wave (in seconds).
        beta (float): Constant to avoid numerical instability.

    Returns:
        tuple: (BPZ, tP1, tE1)
            - BPZ (float): Beginning of the potential zone (in seconds).
            - tP1 (float): Potential arrival time (in seconds).
            - tE1 (float): Associated error (in seconds).
    """
    data = trace.data
    fs = trace.stats.sampling_rate
    N = len(data)

    # Window lengths in samples
    Lb = int(4 * Td * fs)
    La = int(Td * fs)
    d = int(0.6 * Td * fs)
    Ld = int((1 - 0.6) * Td * fs)

    # Initialize arrays for BEA, AEA, DEA
    BEA = np.zeros(N)
    AEA = np.zeros(N)
    DEA = np.zeros(N)

    # Calculate energies
    for t in range(N):
        # BEA calculation with bounds checking
        if (t - Lb) >= 0:
            window = data[max(0, t - Lb):t]
        else:
            window = data[:t]
        
        if len(window) > 0:
            BEA[t] = np.mean(window ** 2)
        else:
            BEA[t] = beta
        
        # AEA calculation
        aea_window = data[t:min(t + La, N)]
        if len(aea_window) > 0:
            AEA[t] = np.mean(aea_window ** 2)
        else:
            AEA[t] = beta
        
        # DEA calculation
        if (t + d) < N:
            dea_window = data[min(t + d, N):min(t + d + Ld, N)]
            if len(dea_window) > 0:
                DEA[t] = np.mean(dea_window ** 2)
            else:
                DEA[t] = 0
        else:
            DEA[t] = 0

    # Avoid division by zero
    BEA[BEA == 0] = beta

    # Calculate energy ratios
    ER1 = AEA / (BEA + beta)
    ER2 = DEA / (BEA + beta)
    CF_mnw = ER1 + ER2

    # Smooth CF_mnw
    window_length = int(0.5 * Td * fs)
    if window_length % 2 == 0:
        window_length += 1  # Ensure odd length for savgol_filter
    
    # Ensure window length is valid
    window_length = max(3, min(window_length, len(CF_mnw)))
    if window_length % 2 == 0:
        window_length -= 1
    
    if window_length >= 3 and len(CF_mnw) >= window_length:
        SCF_mnw = signal.savgol_filter(CF_mnw, window_length, 2)
    else:
        # Fallback to simple smoothing if savgol_filter can't be applied
        SCF_mnw = CF_mnw.copy()

    # Dynamic threshold
    sigma = np.std(CF_mnw[:int(0.5 * N)])
    Thr = 2 + 3 * sigma

    # Detect BPZ (beginning of the potential zone)
    BPZ_indices = np.where(SCF_mnw > Thr)[0]
    BPZ = BPZ_indices[0] / fs if len(BPZ_indices) > 0 else 0

    # Search for local maxima after BPZ
    search_window = int(1.5 * Td * fs)
    start_search = int(BPZ * fs)
    end_search = min(start_search + search_window, N)
    local_max_indices = signal.argrelextrema(SCF_mnw[start_search:end_search], np.greater)[0]
    local_max_values = SCF_mnw[start_search:end_search][local_max_indices]

    if len(local_max_values) > 0:
        tP1_index = start_search + local_max_indices[np.argmax(local_max_values)]
        tP1 = tP1_index / fs
    else:
        tP1 = BPZ

    # Estimate error
    if len(local_max_indices) > 1:
        tE1 = max(
            abs(BPZ - (start_search + local_max_indices[0]) / fs),
            abs((start_search + local_max_indices[0] - start_search + local_max_indices[1]) / fs),
        )
    else:
        tE1 = abs(BPZ - tP1)

    return BPZ, tP1, tE1

def hos_picker(trace, tP1, tE1, Td):
    """
    Implements the Higher Order Statistics (HOS) method using kurtosis to refine picking.

    Args:
        trace (obspy.Trace): Seismic trace.
        tP1 (float): Potential arrival time from MNW (in seconds).
        tE1 (float): Error associated with tP1 (in seconds).
        Td (float): Dominant period of the P-wave (in seconds).

    Returns:
        tuple: (tP2, tE2)
            - tP2 (float): Potential arrival time (in seconds).
            - tE2 (float): Associated error (in seconds).
    """
    data = trace.data
    fs = trace.stats.sampling_rate

    # Window size for kurtosis
    Nk = max(int(2 * tE1 * fs), 1)
    Nk = min(Nk, int(2 * Td * fs))

    # Calculate kurtosis
    CF_k = np.zeros(len(data))
    for t in range(Nk, len(data)):
        window = data[t - Nk : t]
        if len(window) >= 3:  # Need at least 3 points for meaningful kurtosis
            try:
                CF_k[t] = stats.kurtosis(window, fisher=True)
                # Handle potential NaN or infinite values
                if not np.isfinite(CF_k[t]):
                    CF_k[t] = 0.0
            except Exception:
                CF_k[t] = 0.0
        else:
            CF_k[t] = 0.0

    # Smooth CF_k
    window_length = int(0.5 * Td * fs)
    if window_length % 2 == 0:
        window_length += 1
    
    # Ensure window length is valid
    window_length = max(3, min(window_length, len(CF_k)))
    if window_length % 2 == 0:
        window_length -= 1
    
    if window_length >= 3 and len(CF_k) >= window_length:
        SCF_k = signal.savgol_filter(CF_k, window_length, 2)
    else:
        SCF_k = CF_k.copy()

    # Baillard transformation
    SCF_Bk = -SCF_k

    # Search for local minimum around tP1
    search_window = int(tE1 * fs + Td * fs)
    start_idx = max(0, int((tP1 - tE1) * fs))
    end_idx = min(len(data), int((tP1 + Td) * fs))
    
    # Ensure valid search window
    if start_idx >= end_idx or end_idx > len(SCF_Bk):
        tP2 = tP1  # Fallback to original pick
        tE2 = tE1
        return tP2, tE2
    
    search_window_data = SCF_Bk[start_idx:end_idx]
    if len(search_window_data) == 0:
        tP2 = tP1
        tE2 = tE1
        return tP2, tE2
    
    local_min_index = start_idx + np.argmin(search_window_data)
    tP2 = local_min_index / fs
    
    # Calculate error more robustly
    try:
        cf_search_window = CF_k[start_idx:end_idx]
        if len(cf_search_window) > 0:
            max_idx = np.argmax(cf_search_window)
            tE2 = abs(max_idx / fs - (local_min_index - start_idx) / fs)
        else:
            tE2 = tE1
    except Exception:
        tE2 = tE1

    return tP2, tE2

def aic_picker(trace, tP1, tP2, tE1, tE2):
    """
    Implements the Akaike Information Criterion (AIC) method to refine picking.

    Args:
        trace (obspy.Trace): Seismic trace.
        tP1 (float): Potential arrival time from MNW (in seconds).
        tP2 (float): Potential arrival time from HOS (in seconds).
        tE1 (float): Error associated with tP1 (in seconds).
        tE2 (float): Error associated with tP2 (in seconds).

    Returns:
        tuple: (tP3, tE3)
            - tP3 (float): Potential arrival time (in seconds).
            - tE3 (float): Associated error (in seconds).
    """
    data = trace.data
    fs = trace.stats.sampling_rate

    # Search window for AIC
    SW3 = 2 * max(tE1, tE2)
    center = 0.5 * (tP1 + tP2)
    start_idx = max(0, int((center - SW3 / 2) * fs))
    end_idx = min(len(data), int((center + SW3 / 2) * fs))

    # Calculate AIC function
    CF_aic = np.zeros(len(data))
    for t in range(1, len(data) - 1):
        if t > 0 and t < len(data):  # Ensure valid indices
            var1 = np.var(data[:t])
            var2 = np.var(data[t:])
            
            # Add small epsilon to avoid log(0) and handle constant signals
            epsilon = 1e-10
            var1 = max(var1, epsilon)
            var2 = max(var2, epsilon)
            
            CF_aic[t] = t * np.log(var1) + (len(data) - t) * np.log(var2)

    # Normalize Akaike weights
    if start_idx >= end_idx or end_idx > len(CF_aic):
        # Invalid range, return center of search window
        tP3 = center
        tE3 = SW3 / 4  # Default error
        return tP3, tE3
    
    aic_window = CF_aic[start_idx:end_idx]
    if len(aic_window) == 0:
        tP3 = center
        tE3 = SW3 / 4
        return tP3, tE3
    
    min_CF_aic = np.min(aic_window)
    Delta = aic_window - min_CF_aic
    
    # Handle potential numerical issues
    exp_values = np.exp(-Delta / 2)
    sum_exp = np.sum(exp_values)
    
    if sum_exp == 0 or not np.isfinite(sum_exp):
        # Fallback to uniform weights
        AW = np.ones(len(aic_window)) / len(aic_window)
    else:
        AW = exp_values / sum_exp

    # Calculate weighted average arrival time
    indices = np.arange(start_idx, end_idx)
    if len(indices) == 0 or len(AW) == 0:
        tP3 = center
        tE3 = SW3 / 4
        return tP3, tE3
    
    sum_weights = np.sum(AW)
    if sum_weights == 0:
        tP3 = center
        tE3 = SW3 / 4
        return tP3, tE3
    
    tP3 = np.sum(AW * indices / fs) / sum_weights

    # Estimate error
    threshold = 0.1 * np.max(AW)
    error_indices = np.where(AW > threshold)[0]
    tE3 = (error_indices[-1] - error_indices[0]) / fs if len(error_indices) > 0 else 0

    return tP3, tE3

def calculate_snr(trace, pick_time, Td):
    """
    Calculates the signal-to-noise ratio (SNR) around an arrival time.

    Args:
        trace (obspy.Trace): Seismic trace.
        pick_time (float): Arrival time (in seconds).
        Td (float): Dominant period of the P-wave (in seconds).

    Returns:
        float: Signal-to-noise ratio in dB.
    """
    fs = trace.stats.sampling_rate
    noise_window_start = max(0, int((pick_time - 3 * Td) * fs))
    noise_window_end = int(pick_time * fs)
    signal_window_start = int(pick_time * fs)
    signal_window_end = min(len(trace.data), int((pick_time + Td) * fs))

    # Ensure valid windows
    if noise_window_end <= noise_window_start:
        noise_window_end = noise_window_start + max(1, int(0.1 * Td * fs))
    
    if signal_window_end <= signal_window_start:
        signal_window_end = signal_window_start + max(1, int(0.1 * Td * fs))
    
    # Extract windows and calculate RMS
    noise_data = trace.data[noise_window_start:min(noise_window_end, len(trace.data))]
    signal_data = trace.data[signal_window_start:min(signal_window_end, len(trace.data))]
    
    if len(noise_data) == 0 or len(signal_data) == 0:
        return 0  # Cannot calculate SNR
    
    noise_rms = np.sqrt(np.mean(noise_data ** 2))
    signal_rms = np.sqrt(np.mean(signal_data ** 2))
    
    # Add small epsilon to avoid division by zero
    epsilon = 1e-12
    noise_rms = max(noise_rms, epsilon)
    
    if signal_rms > 0:
        return 20 * np.log10(signal_rms / noise_rms)
    else:
        return 0

def adaptive_picker(trace, Td):
    """
    Integrates the three methods (MNW, HOS, AIC) for adaptive picking.

    Args:
        trace (obspy.Trace): Seismic trace.
        Td (float): Dominant period of the P-wave (in seconds).

    Returns:
        tuple: (tP_final, tE_final)
            - tP_final (float): Final arrival time (in seconds).
            - tE_final (float): Associated error (in seconds).
    """
    # Validate input
    if trace is None or len(trace.data) == 0 or Td <= 0:
        return None, None
    
    try:
        BPZ, tP1, tE1 = mnw_picker(trace, Td)
        tP2, tE2 = hos_picker(trace, tP1, tE1, Td)
        tP3, tE3 = aic_picker(trace, tP1, tP2, tE1, tE2)
    except Exception:
        # If any picker fails, return None
        return None, None

    # Check for NaN or invalid values
    picks = [tP1, tP2, tP3]
    valid_picks = []
    valid_Qs = []

    for i, pick in enumerate(picks):
        if (pick is not None and not np.isnan(pick) and 
            np.isfinite(pick) and pick >= 0 and 
            pick < len(trace.data) / trace.stats.sampling_rate):
            try:
                Q = calculate_snr(trace, pick, Td)
                if Q > -50 and np.isfinite(Q):  # Reasonable SNR range
                    valid_picks.append(pick)
                    valid_Qs.append(max(0.1, Q))  # Ensure positive weight
            except Exception:
                continue

    if len(valid_picks) == 0:
        return None, None

    # Calculate weighted average with robust error handling
    try:
        if len(valid_Qs) > 0 and all(w > 0 for w in valid_Qs):
            tP_final = np.average(valid_picks, weights=valid_Qs)
        else:
            tP_final = np.mean(valid_picks)
        
        if len(valid_picks) > 1:
            tE_final = np.std(valid_picks)
        else:
            tE_final = Td / 4  # Default error based on dominant period
            
        # Validate final result
        if not np.isfinite(tP_final) or tP_final < 0:
            return None, None
            
    except Exception:
        return None, None

    return tP_final, tE_final