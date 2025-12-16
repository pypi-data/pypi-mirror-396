from packaging import version
import numpy as np
from geodesic.utils import DeferredImport
import shapely
from shapely.geometry import Polygon
from shapely.strtree import STRtree

measure = DeferredImport("skimage.measure")

# Check shapely major version
SHAPELY_MAJOR = version.parse(shapely.__version__).major


def extract_polygons(
    x: np.ndarray,
    value=None,
    threshold_func=None,
    min_area=1.0,
    simplify_threshold=1.0,
    pad_border=True,
):
    if x.ndim != 2:
        raise ValueError(f"extract_polygons only works on 2D arrays, got {x.ndim}")

    y = x
    if threshold_func is not None:
        y = threshold_func(x)
    elif value is not None:
        y = x == value

    if pad_border:
        rows, cols = y.shape
        z = np.zeros((rows + 2, cols + 2), dtype=y.dtype)
        z[1 : rows + 1, 1 : cols + 1] = y
    else:
        z = y

    contours = measure.find_contours(z, level=0.5)

    rows, cols = x.shape

    shapes = [
        Polygon(
            shell=zip(
                (np.maximum(contour[:, 1] - pad_border, 0)) / cols,
                (np.maximum(contour[:, 0] - pad_border, 0)) / rows,
            )
        )
        for contour in contours
        if len(contour) > 2
    ]

    # filter based on area
    shapes = [
        shape
        for shape in shapes
        if (
            shape.area > (min_area / (cols - 1) / (rows - 1))
            and shape.exterior.coords[0] == shape.exterior.coords[-1]
        )
    ]
    # simplify - use a simplify threshold in pixels, convert to normalized tile coordinate distance
    distance_convert = np.sqrt(rows * rows + cols * cols)
    shapes = [shape.simplify(simplify_threshold / distance_convert) for shape in shapes]
    # filter out invalid polygons
    shapes = [shape for shape in shapes if shape.is_valid]

    # Figure out which contours are holes and which are exterior rings, create full polygons.
    exterior_rings = [geom.exterior for geom in shapes if geom.exterior.is_ccw]
    interior_rings = [geom.exterior for geom in shapes if not geom.exterior.is_ccw]

    idx = STRtree(interior_rings)

    geoms = []
    for exterior_ring in exterior_rings:
        if SHAPELY_MAJOR == 1:
            interiors = [ring for ring in idx.query(exterior_ring)]
        else:
            interiors = [interior_rings[i] for i in idx.query(exterior_ring)]
        geom = Polygon(shell=exterior_ring, holes=interiors).buffer(0)
        geoms.append(geom)

    return [g for g in geoms if len(g.exterior.coords) > 0]
