import numpy as np
from fast_histogram import histogram2d
import evosegment.utils as utils
from evosegment.labelling import labelHistogram
import matplotlib.pyplot as plt
import scipy.spatial.distance
import scipy.ndimage as ndi
from scipy.signal import find_peaks
import itertools
from matplotlib.widgets import PolygonSelector
from matplotlib.patches import Polygon

def make2DHistogram(im0, im1, bins):
    """
    Compute a 2D histogram from two or more input images.

    Args:
        im0 (ndarray): First input image.
        im1 (ndarray): Second input image. This can be an array of images to concatenate.
        bins (int or [int,int]): Number of bins for each dimension of the histogram .

    Returns:
        tuple: A tuple containing the following elements:
            - H (ndarray): The 2D histogram.
            - ie (ndarray): Bin edges for the first input image.
            - je (ndarray): Bin edges for the second input image.

    Notes:
        - The function computes a 2D histogram by binning the pixel values of `im0` and `im1`.
        - The `bins` parameter controls the number of bins to use in each dimension.
        - The range of the histogram bins is determined by the minimum and maximum values of the input images.
        - The computed histogram `H` represents the joint distribution of pixel intensities between `im0` and `im1`.
        - The `ie` and `je` arrays contain the bin edges corresponding to the first and second input images, respectively.
    """

    # check if im1 is a list of images
    if im1.ndim != im0.ndim:
        im0 = np.asarray([im0] * im1.shape[0])
    # minval = min(im0.min(),im1.min())
    # maxval = max(im0.max(),im1.max())+1 #to catch the last bin
    binrange = [(im1.min(), im1.max()), (im0.min(), im0.max())]
    H = histogram2d(im1.flatten(), im0.flatten(), bins=bins, range=binrange)  # im0 on x im1 on y
    # Pad histogram to be able to peaksearch the edges
    H = np.pad(H, pad_width=[(1, 1), (1, 1)], mode='constant')
    # bin centers
    if not isinstance(bins, list):
        bins = [bins, bins]
    ie = np.linspace(im1.min(), im1.max(), num=bins[0] + 1)
    je = np.linspace(im0.min(), im0.max(), num=bins[1] + 1)
    ic = utils.computeBinCenters(ie)
    jc = utils.computeBinCenters(je)
    return H, ic, jc


class PickClusters:
    """Class for picking cluster positions by clicking in a figure"""

    def __init__(self, figure, r):
        ### TODO: Figure out how to set the radius of the circle interactively
        self.figure = figure  # this is where the circle lives
        self.centroid = []
        self.rs = []
        self.r = r  # remove once the todo is fixed

    def connect(self):
        self.press = self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.release = self.figure.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        self.centroid.append((event.ydata, event.xdata))
        self.rs.append(self.r)  # this should be updated interectively

    def on_release(self, event):
        c = plt.Circle((event.xdata, event.ydata), self.rs[-1], color='b', fill=False)
        self.figure.gca().add_patch(c)


class PolygonClusters:
    """Class for drawing polygons around the clusters in a joint histogram"""
    
    def __init__(self, figure):
        self.figure = figure
        self.ax = figure.gca()
        self.vertices = []
        self.selector = PolygonSelector(self.ax, self.onselect)
        print("Draw polygons around clusters. Close the polygon by clicking on the starting point. Press 'esc' to start a new polygon.")
        
    def onselect(self,vertices):
        # Save the vertices
        self.vertices.append(vertices)
        # Draw the polygon permanently on the axes
        poly = Polygon(vertices, closed=True, fill=False, edgecolor='blue', linewidth=2)
        self.ax.add_patch(poly)
        plt.draw()  # Refresh the figure
        # Reset selector for next polygon
        self.selector._selection_completed = False
        self.selector._xs = []
        self.selector._ys = []
        self.selector._polygon = None



def detectClusterCenters(
    H,
    diagonalwidth=3,
    halfstripwidth=4,
    kd=10000,
    kod=1000,
    diag_od_threshold=1,
    plot=False,
    verbose=False,
    filter=False,
    filterpars=(3, 1),
):
    """
    Detects cluster centers (peaks) in a 2D histogram.

    The function applies smoothing to the diagonal of the histogram, identifies peaks in the smoothed diagonal,
    and extracts additional peaks in vertical strips around each diagonal peak. It also includes a peak in the
    bottom row of the histogram to account for padding during registration.

    Parameters:
        H (ndarray): 2D histogram array.
        diagonalwidth (int): Optional. Width of band extracted along the diagonal of H for finding peaks. Default=3.
        halfstripwidth (int): Optional. Half-width of the vertical band extracted around the diagonal clusters. Defaul=2.
        kd (int): Optional. Threshold on number of pixels in the peak for accepting a peak on the diagonal. Defalt = 10000
        kod (int): Optional. Threshold on number of pixels in the peak for accepting a peak off the diagonal. Defalt = 1000
        filter (bool): Optional. If True performs savgol filtering before peaksearching
        filterpars (tuple): Optional. Tuple of (window_length, order) for the savgol filter. Default =(3,1)
        diag_od_threshold (float): Optional. Min distance between on- and off-diagonal clusters

    Returns:
        tuple: A tuple containing the number of detected cluster centers and an array of their coordinates.
            - The coordinate array has shape (N, 2), where N is the number of clusters detected.
              Each row represents a cluster and contains the row and col coordinates.

    """
    diag = utils.sumDiagonalBand(H, diagonalwidth)
    diag_peaks = utils.findAndFilterPeaks(diag, k=kd, plot=plot, verbose=verbose, filter=filter, filterpars=filterpars)
    if verbose:
        print('diag_peaks:', diag_peaks, '\n')
    peaks = [[p, p] for p in diag_peaks]
    distance = lambda x1, x2: np.sqrt((x1 - x2) ** 2)
    for p in diag_peaks:
        if halfstripwidth == 0:
            col = H[:, p]
        else:
            start = np.max([p - halfstripwidth, 0])
            stop = np.min([p + halfstripwidth, H.shape[1]])
            col = H[:, start:stop]  # Take a vertical strip at the peak to increase signal-to-noise
            col = np.mean(col, axis=-1)
        odp = utils.findAndFilterPeaks(col, k=kod, plot=plot, verbose=verbose, filter=filter, filterpars=filterpars)
        if verbose:
            print(f'Peaks at column {p}:', odp, '\n')
        if len(odp) > 0:
            for op in odp:
                if distance(p, op) > diag_od_threshold:
                    peaks.append([op, p])  # sometimes the diagonal peak is not found. Depends on the peak shape

    # # Add a peaks in the bottom row of the histogram to account for padding during registration
    # row = H[0, :]
    # peaks.append([[0,np.argmax(row)]])
    peaks = np.asarray(peaks)
    if verbose:
        print('These are all peaks:\n', peaks)
        print(f'{peaks.shape[0]:d} peaks found')
    return peaks.shape[0], peaks


def subtractive_mountain_clustering(ra, rb, eps_u, eps_b, threshold, histogram, plot=True):
    """
    Perform subtractive mountain clustering on a 2D histogram.

    Args:
        ra (float): Parameter controlling the width of the influence region for the cluster centers.
        rb (float): Parameter controlling the width of the influence region for reducing potential near existing cluster centers.
        eps_u (float): Threshold ratio for accepting a potential point as a cluster center.
        eps_b (float): Threshold ratio for rejecting a potential point as a cluster center.
        threshold (float): Threshold value for considering a histogram bin as a potential point.
        histogram (ndarray): 2D histogram array representing the data.
        plot (bool): Whether to plot the potential map and cluster centers.

    Returns:
        tuple: A tuple containing the following elements:
            - nclusters (int): The number of clusters found in the histogram.
            - centers (ndarray): An ndarray containing the coordinates of the cluster centers.

    Notes:
        - The subtractive mountain clustering algorithm aims to find clusters in the given histogram.
        - The `ra` parameter controls the width of the influence region for the cluster centers.
        - The `rb` parameter controls the width of the influence region for reducing potential near existing cluster centers.
        - The `eps_u` and `eps_b` parameters determine the threshold ratios for accepting and rejecting potential points as cluster centers, respectively.
        - The `threshold` parameter defines the value threshold for considering a histogram bin as a potential point.
        - The `histogram` parameter is a 2D ndarray representing the data to be clustered.
        - The `plot` parameter specifies whether to visualize the potential map and cluster centers.
        - The function returns a tuple containing the number of clusters and their coordinates.

    """
    alpha = 4 / (ra**2)
    beta = 4 / (rb**2)

    r_coords, c_coords = np.meshgrid(range(histogram.shape[0]), range(histogram.shape[1]), indexing='ij')
    coordinates = np.column_stack((r_coords.flatten(), c_coords.flatten()))
    data = histogram.flatten()
    idx = np.where(data >= threshold)

    Pi = np.zeros(histogram.shape[0] * histogram.shape[1])
    centers = [[0,0]]  #start with a cluster for the background

    distances = scipy.spatial.distance.cdist(np.array(coordinates), np.array(coordinates[idx]))
    for i, cdist in enumerate(distances):
        Pi[i] = np.sum(np.exp(-alpha * np.square(cdist)))

    ii = np.argmax(Pi)
    centers.append([coordinates[ii][0], coordinates[ii][1]])
    Pstar = Pi[ii]
    retstat = 1
    while retstat > 0:
        dist_cen = scipy.spatial.distance.cdist(np.array(coordinates), np.array(centers[-1:]))
        ii = np.argmax(Pi)
        Pks = Pi[ii]
        for i, cdist in enumerate(dist_cen):
            Pi[i] -= Pks * np.exp(-beta * np.square(cdist))
        retstat, centers, Pi = _selection_criteria(coordinates, centers, Pi, Pstar, eps_u, eps_b, ra)

    centers = np.array(centers)
    nclusters = centers.shape[0]
    if plot:
        plt.figure()
        plt.imshow(Pi.reshape(histogram.shape), origin='lower')
        plt.scatter(centers[:, 1], centers[:, 0], marker='o')
        plt.show()

    return nclusters, centers


def _selection_criteria(coordinates, centers, Pi, Pstar, eps_u, eps_b, ra):
    retstat = 2
    while retstat == 2:
        ii = np.argmax(Pi)
        Pks = Pi[ii]
        if Pks > eps_u * Pstar:
            centers.append([coordinates[ii][0], coordinates[ii][1]])
            retstat = 1  # found an acceptable cluster
        elif Pks < eps_b * Pstar:
            retstat = 0  # no more clusters
        else:
            ds = scipy.spatial.distance.cdist(np.array(centers), np.array([coordinates[ii]]))
            dmin = np.min(ds)
            if dmin / ra + Pks / Pstar >= 1:
                centers.append([coordinates[ii][0], coordinates[ii][1]])
                retstat = 1
            else:
                Pi[ii] = 0
    return retstat, centers, Pi


def kmeans_clustering(H, kcentroids, threshold=0, plot=False, verbose=False, return_cmap=False, maxiter=30):
    """
    Performs k-means clustering on a 2D histogram.

    Args:
        H (ndarray): The 2D histogram.
        kcentroids (ndarray): Initial cluster centroids.
        threshold (int, optional): Threshold for labeling a bin. Defaults to 0.
        plot (bool, optional): Whether to plot the results. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
        return_cmap (bool, optional): Whether to return the colormap used for the label plot.
        max_iter (int, optional): Max number of iterations to perform. Defaults to 30.
    Returns:
        tuple: A tuple containing the following elements:
            - updated_centroids (ndarray): An ndarray containing the updated cluster centroids.
            - labels (ndarray): An ndarray of the same shape as `H`, representing the labels assigned to each point in the histogram.
            - cmap (ListedColormap): (optional) A `ListedColormap` object representing the colormap used for the label plot.

    """
    nclusters = len(kcentroids)
    residual = 1
    niter = 0
    # for _ in range(2 * nclusters):
    while residual > 1e-3 and niter < maxiter:
        # Expectation step
        labels = labelHistogram(H, kcentroids, threshold=threshold)

        # if niter > 0:
        # n0 = nl
        k0 = kcentroids.copy()
        nl = np.array([np.sum(labels == l) for l in range(nclusters + 1)])
        # Maximization step
        # k0 = kcentroids #save from previous iteration
        kcentroids = ndi.center_of_mass(H, labels=labels, index=range(1, nclusters + 1))
        kcentroids = np.array(kcentroids)
        if verbose:
            print('----')
            print(nl)
            print(kcentroids)
        if niter > 0:
            residual = np.linalg.norm(kcentroids - k0)  # TODO: better stopping criteria?
            print(residual)
        niter += 1
        if verbose:
            print(f'Iteration: {niter}, residual: {residual:.3e}')

    if not niter < maxiter:
        print('Warning k-means stopped du to max iterations.')

    cmap = utils.make_cmap(nclusters)

    if plot:
        plt.figure()
        plt.imshow(labels, origin='lower', cmap=cmap)
        for i, j in kcentroids:
            plt.scatter(j, i)
        plt.xlabel('Reference image')
        plt.ylabel('Evolved image')
    if return_cmap:
        return kcentroids, labels, cmap
    return kcentroids, labels


def grid_clusters(im1, im2, mask=None, prominence=(None, None), wlen=11, nbins=128, plot=False):
    """
    Identify clusters in two images based on separete histogram peak detection and subsequent gridding of the peaks.

    Parameters:
    im1 : array-like
        First input image.
    im2 : array-like
        Second input image.
    mask : array-like, optional
        Mask to apply to the histograms for normalization.
    prominence : tuple of float or None, optional
        Required prominence of peaks in the histograms for im1 and im2.
    wlen : int, optional
        Minimum width to determine the prominence of the peaks.
    nbins : int, optional
        Number of bins for the histograms.
    plot : bool, optional
        If True, plot the histograms and detected peaks.

    Returns:
    nclusters : int
        Number of detected clusters.
    centroids : ndarray
        Array of centroid coordinates for the detected clusters.
    """
    H1, im1_bins = np.histogram(im1, bins=nbins)
    H2, im2_bins = np.histogram(im2, bins=nbins)
    H1pad = np.pad(H1, pad_width=[(1, 1)], mode='constant', constant_values=(H1[1], H1[-2]))
    H2pad = np.pad(H2, pad_width=[(1, 1)], mode='constant', constant_values=(H2[1], H2[-2]))

    # Correct for mask
    if mask is not None:
        H1 = H1 / np.sum(mask)
        H2 = H2 / np.sum(mask)

    H1peaks = find_peaks(H1pad, prominence=prominence[0], wlen=wlen)[0]
    H1peaks = [x - 1 for x in H1peaks[1:]]  # remove the peak at 0
    H2peaks = find_peaks(H2pad, prominence=prominence[1], wlen=wlen)[0]
    H2peaks = [x - 1 for x in H2peaks[1:]]

    centroids = itertools.product(H2peaks, H1peaks)
    centroids = np.array(list(centroids))
    nclusters = len(centroids)

    if plot:
        im1_center = 0.5 * (im1_bins[1:] + im1_bins[:-1])
        im2_center = 0.5 * (im2_bins[1:] + im2_bins[:-1])
        im1_w = 0.7 * np.diff(im1_bins)[0]
        im2_w = 0.7 * np.diff(im2_bins)[0]

        fig, ax = plt.subplots(1, 2)
        ax[0].bar(im1_center, H1, align='center', width=im1_w, edgecolor='none')
        [ax[0].axvline(x=im1_center[i], color='k', ls='--') for i in H1peaks]

        ax[1].bar(im2_center, H2, align='center', width=im2_w, edgecolor='none')
        [ax[1].axvline(x=im2_center[i], color='k', ls='--') for i in H2peaks]

    return nclusters, centroids
