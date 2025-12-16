"""Signal processing module."""

import numpy as np


def _find_barycenters_fast(
    fxx: np.ndarray, sxx: np.ndarray, freq_window: float
) -> np.ndarray:
    max_f_idx = np.argmax(sxx, axis=0)
    bary_win_size = int(freq_window / np.mean(np.diff(fxx)))
    # sxx is nfreqs x ntimes
    # Create indices for all freq-windows at each time so dimensions :
    # winsize x ntimes
    # Indices are -30:30 centered on each max freq
    indices = (
        np.arange(-bary_win_size, bary_win_size + 1)[..., np.newaxis]
        + max_f_idx[np.newaxis, ...]
    )
    # Make sure indices are in range
    indices = np.clip(indices, 0, sxx.shape[0] - 1)
    # Extract windows for all columns. We need cols_indexer to select all columns of
    # the spectrogram and pair them with the frequency indices
    cols_indexer = np.arange(sxx.shape[1])
    sxx_windows = sxx[indices, cols_indexer]
    fxx_windows = fxx[indices]
    # Compute barycenters
    sum_weight_f = np.sum(fxx_windows * sxx_windows, axis=0)
    sum_weight = np.sum(sxx_windows, axis=0)

    return sum_weight_f / sum_weight


def _find_barycenters_slow(
    fxx: np.ndarray, sxx: np.ndarray, freq_window: float
) -> np.ndarray:
    max_f_idx = np.argmax(sxx, axis=0)
    bary_win_size = int(freq_window / np.mean(np.diff(fxx)))
    barycenters = np.zeros(max_f_idx.size)
    for idx in range(max_f_idx.size):
        indexer = slice(max_f_idx[idx] - bary_win_size, max_f_idx[idx] + bary_win_size)
        sum_weight_f = np.sum(fxx[indexer] * sxx[indexer, idx])
        sum_weight = np.sum(sxx[indexer, idx])
        barycenters[idx] = sum_weight_f / sum_weight

    return barycenters


def find_barycenters(
    fxx: np.ndarray, sxx: np.ndarray, freq_window: float, fast: bool = True
) -> np.ndarray:
    """
    Compute the barycenters of the maximum frequencies over time in a spectrogram.

    It uses the spectrogram from `scipy.signal.spectrogram()`.

    Parameters
    ----------
    fxx : np.ndarray
        Array with the frequencies of the spectrogram, as returned by
        `scipy.signal.spectrogram()`.
    sxx : np.ndarray
        Spectrogram as returned by `scipy.signal.spectrogram()`.
    freq_window : float
        Frequency-window size around the frequency maxima, in the same units as `fxx`.
    fast : bool, optional
        Whether to use the vectorized version of the algorithm, default is True.
    """
    if fast:
        barycenters = _find_barycenters_fast(fxx, sxx, freq_window)
    else:
        barycenters = _find_barycenters_slow(fxx, sxx, freq_window)

    return barycenters


def find_nearest_index(array: np.ndarray, value: float) -> int:
    """
    Find the index of the nearest value in `array` to the input `value`.

    Parameters
    ----------
    array : np.ndarray
        Array from which the index is extracted from.
    value : float
        Value to find in `array`.
    """
    return (np.abs(array - value)).argmin()


def get_up_down_indices(x: np.ndarray) -> tuple[slice, slice]:
    """
    Get indices in `y` for increasing and decreasing `x`.

    Returns 2 slices, the first indexes `y` in increasing `x`, the second in decreasing
    `x`. `x` should be a vector that increases, reach a maximum, then decreases.

    Parameters
    ----------
    x : np.ndarray
        Should be 1D.

    Returns
    -------
    slice_inc, slice_dec : slice
    """
    idx_at_xmax = np.argmax(x)
    return (slice(0, idx_at_xmax), slice(-1, idx_at_xmax - 1, -1))


def split_up_down(
    x: np.ndarray, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split `y` in two arrays based on if `x` is increasing or decreasing.

    `x` should be a vector that increases, reaches a maximum and then decreases (e.g. a
    magnetic field).
    One array corresponds to increasing `x`, the othe corresponds to decreasing `x`. The
    arrays are sorted and the `x` arrays are also returned.

    Parameters
    ----------
    x, y : np.ndarray
        1D vectors.

    Returns
    -------
    x_inc, y_inc : np.ndarray
        `x` and `y` when `x` increases.
    x_dec, y_dec : np.ndarray
        `x` and `y` when `x` decreases.
    """
    s_inc, s_dec = get_up_down_indices(x, y)
    return (x[s_inc], y[s_inc], x[s_dec], y[s_dec])


def fit_poly(
    field: np.ndarray,
    sig: np.ndarray,
    boundary1: float,
    boundary2: float,
    poly_deg: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Polynomial fit of `sig(field)`, between boundaries.

    Returns the resulting polynome evaluated at `field` along with the detrended signal.

    Parameters
    ----------
    field : np.ndarray
        Magnetic field vector (x).
    sig : np.ndarray
        Signal vector (y).
    poly_boundary1, poly_boundary2 : float
        Do the fit only in `field` comprised in `[poly_boundary1, poly_boundary2]`.
    poly_deg : int
        Polynome degree.

    Returns
    -------
    poly : np.ndarray
        Polynome evaluated at `field`.
    sig_detrend : np.ndarray
        `sig` subtracted
    """
    idx_bmin = find_nearest_index(field, boundary1)
    idx_bmax = find_nearest_index(field, boundary2)

    fit = np.polynomial.Polynomial.fit(
        field[idx_bmin:idx_bmax],
        sig[idx_bmin:idx_bmax],
        poly_deg,
    )
    res = fit(field)
    return res, sig - res


def interpolate_inverse(
    x: np.ndarray, y: np.ndarray, boundary1: float, boundary2: float, npoints: int
) -> tuple[np.ndarray, np.ndarray]:
    """
    Oversample `y` in `1/x` in the given range.

    Parameters
    ----------
    x : np.ndarray
        Points at which `y` is evaluated.
    y : np.ndarray
        Signal to oversample.
    boundary1, boundary2 : float
        Define the range to select and oversample, before inversion.
    npoints : int
        Number of points of the resulting vectors.

    Returns
    -------
    x_inverse_oversample : np.ndarray
        `1/x` oversampled in `[1/boundary2, 1/boundary1]`.
    y_oversample : np.ndarray
        `y` oversampled in `[1/boundary2, 1/boundary1]`.
    """
    # Create the oversampled time vector
    x_inverse_oversample = np.linspace(
        1 / boundary2, 1.0 / boundary1, npoints, endpoint=False
    )
    # Interpolate
    y_oversample = np.interp(1 / x_inverse_oversample, x, y)

    return x_inverse_oversample, y_oversample


def fourier_transform(
    a: np.ndarray, d: float, pad_mult: int = 1
) -> tuple[np.ndarray, np.ndarray]:
    """
    Fourier transform for 1D real signal, with extra padding.

    Parameters
    ----------
    a : np.ndarray
        Input array.
    d : float
        Sample spacing.
    pad_mult : int, optional
        Multiplier of signal size used for padding. Default is 1.

    Returns
    -------
    freq : np.ndarray
        Frequencies.
    X : np.ndarray
        Magnitude of the fourier transform.
    """
    n = a.size * pad_mult
    X = np.fft.rfft(np.hamming(a.size) * a, n=n)[:-1]
    freq = np.fft.rfftfreq(n, d=d)[:-1]
    X = np.abs(X) * 2 / n
    return freq, X


def collate_arrays(to_save: list[np.ndarray]):
    """
    Store 1D vectors as columns in a 2D arrays.

    Dimension mismatches are filled with trailing NaNs.

    Parameters
    ----------
    to_save : list[np.ndarray]
        List of arrays to save in the same file.

    Returns
    -------
    a : np.ndarray
        The array with all the vectors, with NaNs to fill shorter vectors.
    """
    # Build the array
    ncolumns = len(to_save)
    nrows = max([a.size for a in to_save])
    a_out = np.full((nrows, ncolumns), np.nan)

    # Fill the array
    for idx_col, a in enumerate(to_save):
        a_out[: a.size, idx_col] = a

    return a_out
