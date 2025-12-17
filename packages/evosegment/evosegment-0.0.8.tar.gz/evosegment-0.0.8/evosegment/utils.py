import pickle

import colorcet as cc
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
import scipy.spatial.distance
import scipy.ndimage
import seaborn as sns
import skimage.morphology


def save_segmentation(
    filename,
    H=None,  # 2D histogram
    labels=None,  # labels for each bin in the histogram
    ic=None,  # bin edges for columns
    jc=None,  # bin edges for rows
    cmap=None,  # colormap for the labels
    centroids=None,  # cluster centroids
    nclusters=None,
):  # number of clusters
    """
    Save segmentation results to a file.

    Args:
        filename (str): Path to the output file.
        H (ndarray, optional): 2D histogram. Defaults to None.
        labels (ndarray, optional): Labels for each bin in the histogram. Defaults to None.
        ic (ndarray, optional): Bin centers for horizontal axis. Defaults to None.
        jc (ndarray, optional): Bin centers for vertical axis. Defaults to None.
        cmap (ListedColormap, optional): Colormap for the labels. Defaults to None.
        centroids (ndarray, optional): Cluster centroids. Defaults to None.
        nclusters (int, optional): Number of clusters. Defaults to None.
    """
    res = {  # dictionary containing the results
        'H': H,
        'labels': labels,
        'ic': ic,
        'jc': jc,
        'cmap': cmap,
        'centroids': centroids,
        'nclusters': nclusters,
    }
    with open(filename, 'wb+') as f:
        pickle.dump(res, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_segmentation(filename):
    """
    Load segmentation data from a pickle file.

    Args:
        filename (str): The path to the pickle file.

    Returns:
        dict: A dictionary containing the segmentation data loaded from the file.
    """
    with open(filename, 'rb') as f:
        res = pickle.load(f)
    return res


def make_cmap(ncolors, palette=cc.glasbey_dark):
    return colors.ListedColormap(sns.color_palette(palette, n_colors=ncolors))


def computeBinCenters(edges):
    return (edges[1:] + edges[:-1]) / 2


def sumDiagonalBand(H, w):
    """
    Extracts a band along the diagonal of a square matrix and returns the sum of the diagonals within the band.

    Args:
        H (ndarray): The input histogram as a square matrix.
        w (int): The width of the band. Should probably be be an odd number or 0.

    Returns:
        ndarray: The column-wise sum of the diagonals within the band.

    Raises:
        AssertionError: If `w` is not an odd number.

    Notes:
        - The function assumes that `H` is a square matrix.
        - The band is formed by summing the diagonals within a certain width around the main diagonal.
        - The width of the band is controlled by the `w` parameter.
    """
    # assert w%2==1, "w must be odd"
    # extract (w-1)/2 diagonals on each side
    diags = []
    for i in range((w - 1) // 2 + 1):
        if i == 0:  # main diagonal
            diags.append(np.diag(H))
        else:
            # positive diagonal
            dp = np.diag(H, i)
            dp = np.pad(dp, (i, 0), mode='constant')
            diags.append(dp)
            # negative diagonal
            dn = np.diag(H, -i)
            dn = np.pad(dn, (0, i), mode='constant')
            diags.append(dn)
    # sum the diagonals
    return np.sum(np.asarray(diags), axis=0)


def findAndFilterPeaks(data, k=1000, plot=False, verbose=False, filter=False, filterpars=(3, 1)):
    npix = np.sum(data)
    if filter:
        data = scipy.signal.savgol_filter(data, filterpars[0], filterpars[1])

    peaks, properties = scipy.signal.find_peaks(data)  # ,width=1,height=1)
    widths, wh, lb, rb = scipy.signal.peak_widths(data, peaks, rel_height=0.5)
    peaksums = np.asarray([np.sum(data[int(np.floor(l)) : int(np.ceil(r))]) for l, r in zip(lb, rb)])
    pph = peaksums > k
    peaks = peaks[pph]
    if verbose:
        print(f'The threshold is {k} voxels and there are {int(npix):d} voxels in this subset')
        print('The peaks contains:', peaksums, 'voxels')
        print(f'Keeping these {peaks.shape[0]:d} peaks:', peaks)
    if plot:
        plt.figure()
        plt.plot(data)
        plt.plot(peaks, data[peaks], 'x')
        plt.hlines(wh, lb, rb, color="C2")
    return peaks


def erodeEdges(im, footprintsize=10):
    # Creates a binary mask where the edges are eroded
    footprint = skimage.morphology.cube(footprintsize, decomposition='sequence')
    eroded_mask = skimage.morphology.binary_erosion(im, footprint=footprint)
    eroded_mask = scipy.ndimage.binary_fill_holes(eroded_mask)
    return eroded_mask.astype(np.uint8)

def scaleToBinRange(im,nbins,dtype=np.uint8):
    return np.array(nbins*(1.*im-im.min())/(im.max()-im.min()),dtype=dtype)
