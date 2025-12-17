import scipy.spatial.distance
import numpy as np
import evosegment.utils as utils
from concurrent.futures import ProcessPoolExecutor
import skimage.draw

def labelHistogram(H, vertices=None, centroids=None, threshold=0, make_cmap=False):
    """
    Labels a 2D histogram based on a specified threshold and cluster centroids or vertices. Either vertices or centroids
    must be provided.

    Parameters:
        H (ndarray): 2D histogram array.
        vertices (ndarray): Array of cluster vertices.
        centroids (ndarray): Array of cluster centroids. Each centroid should be a 2D point.
        threshold (float): Threshold value for labeling. Defaults to 0.
        make_cmap (bool): Whether to create and return a colormap for the labels. Defaults to False.

    Returns:
        ndarray: Array with the same shape as the input histogram,
        where each element is a label indicating the bin classification.
        If `make_cmap` is True, also returns a colormap for the labels.

    Raises:
        ValueError: If the input histogram or cluster centroids are not 2D ndarrays.

    """
    if (vertices is not None) and (centroids is not None):
        raise ValueError("Provide either vertices or centroids, not both.")
    elif (vertices is None) and (centroids is None):
        raise ValueError("Either vertices or centroids must be provided.")
   
    if not H.ndim == 2:
        raise TypeError("Input histogram must be a 2D ndarray.")
  
    labels = np.zeros_like(H, dtype=int)
    #Labelling based on centroids
    if centroids is not None:
        if not centroids.ndim == 2:
            raise TypeError("Cluster centroids must be a 2D ndarray.")
        for ii in range(H.shape[0]):
            for jj in range(H.shape[1]):
                if H[ii, jj] >= threshold:
                    rc = [ii + 0.5, jj + 0.5]  # center of the pixel
                    distances = scipy.spatial.distance.cdist([rc], centroids)
                    labels[ii, jj] = np.argmin(distances) + 1
    #Labelling based on vertices
    else:
        for i,v in enumerate(vertices):
            label = i+1
            rr,cc = _find_pixels_in_polygon(v,H.shape)
            labels[rr,cc] = label # assign label to pixels inside polygon. For overlapping polygons, later ones overwrite earlier ones.

    if make_cmap:
        nlabels = labels.max()+1
        cmap = utils.make_cmap(nlabels)
        return labels, cmap
    return labels

def _find_pixels_in_polygon(vertices,shape):
    # Convert vertices to integer pixel coordinates
    vertices = np.asarray(vertices) #np.round(np.asarray(vertices),0).astype(int)
    r,c = vertices[:,1], vertices[:,0]
    rr,cc = skimage.draw.polygon(r, c, shape=shape)
    return rr,cc

def _paintParallel(args):
    im0_chunk, im1_chunk, labels, ic, jc = args
    segmented = np.zeros(im0_chunk.shape)
    for sl, (i0, i1) in enumerate(zip(im0_chunk, im1_chunk)):
        bi = np.digitize(i1, ic, right=True)
        bj = np.digitize(i0, jc, right=True)
        bj[bj == len(jc)] -= 1  # Adjust the last bin index
        bi[bi == len(ic)] -= 1
        # bj = np.where(bj == bj.max(), bj.max() - 1, bj)  # Extend the last bin
        # bi = np.where(bi == bi.max(), bi.max() - 1, bi)
        segmented[sl] = labels[bi, bj]

    return segmented


def paintVolume(im0, im1, labels, ic, jc, slicenr=None, nprocs=1):
    """
    Apply segmentation labels to a volume based on 2d histogram labelling.

    Args:
        im0 (ndarray): First input image volume.
        im1 (ndarray): Second input image volume.
        labels (ndarray): Segmentation labels.
        ic (ndarray): Bin centers for the first image.
        jc (ndarray): Bin centers for the second image.
        slicenr (int, optional): Slice number to segment. If specified, only the slice with this index will be segmented.
        nprocs (int, optional): Number of processes to use for parallel execution. Default is 1.

    Returns:
        ndarray: Segmented volume based on the given image and intensity thresholds.

    Raises:
        ValueError: If the specified slicenr is out of range.

    Notes:
        - The function segments a volume by assigning labels from the `labels` array based on intensity thresholds.
        - If `slicenr` is provided, only that particular slice is segmented, and a 2D segmented slice is returned.
        - If `slicenr` is not provided, the function segments the entire 3D volume in parallel using multiple processes.
          The `nprocs` parameter controls the number of processes to use.
    """
    if slicenr is not None or im0.ndim == 2:
        # Only paint one slice
        if slicenr is not None:
            im0 = im0[slicenr]
            im1 = im1[slicenr]
        segmented = np.zeros(im0.shape)
        bi = np.digitize(im1, ic, right=False)
        bj = np.digitize(im0, jc, right=False)
        bj[bj == len(jc)] -= 1  # Adjust the last bin index
        bi[bi == len(ic)] -= 1

        segmented = labels[bi, bj]
        return segmented

    n_elements = im0.shape[0]
    chunk_size = (n_elements + nprocs - 1) // nprocs
    chunks = [
        (
            im0[i * chunk_size : min((i + 1) * chunk_size, n_elements)],
            im1[i * chunk_size : min((i + 1) * chunk_size, n_elements)],
            labels,
            ic,
            jc,
        )
        for i in range(nprocs)
    ]

    with ProcessPoolExecutor(nprocs) as executor:
        results = list(executor.map(_paintParallel, chunks))
    segmented = np.concatenate(results, axis=0)
    return segmented.astype(np.uint8)
