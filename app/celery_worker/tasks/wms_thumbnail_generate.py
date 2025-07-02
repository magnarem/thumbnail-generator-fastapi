import contextlib
import multiprocessing as mp
import os

import cartopy.crs as ccrs
import matplotlib
import matplotlib.pyplot as plt
from celery import states

# from owslib.util import ParseError, ServiceException
# from lxml.etree import XMLSyntaxError, Error
# from requests.exceptions import Timeout
from celery.exceptions import (
    SoftTimeLimitExceeded,
    TaskError,  # , TimeoutError
)
from celery.utils.log import get_task_logger
from owslib.wms import WebMapService

from ..app import app

matplotlib.use("agg")
logger = get_task_logger(__name__)

blacklist_layers = ("latitude", "longitude", "lat", "lon", "MS")

# logger = logging.getLogger(__name__)
WMS_GENERATE_THUMBNAIL_TASK = "metsis.create_wms_thumbnail_task"


@app.task(
    name=WMS_GENERATE_THUMBNAIL_TASK,
    bind=True,
    soft_time_limit=600,
    max_retries=3,
    ignore_result=False,
)
def create_wms_thumbnail_task(self, wmsconfig):
    logger.info("Staring generate thumbnail_task:")

    # Extracting required fields
    id = wmsconfig["id"]
    wms_url = wmsconfig["wms_url"]
    path = wmsconfig["path"]

    # Optional field default values
    wms_layer: str = None
    wms_style: str = None
    wms_zoom_level: int = 0
    wms_timeout: int = 300
    add_coastlines: bool = True
    projection: str = None
    thumbnail_extent: str = None
    wms_layers_mmd: list = []

    # Extracting optional fields
    if "wms_layer" in wmsconfig:
        wms_layer = wmsconfig["wms_layer"]
        logger.debug("Got overriden wms_layer: %s", wms_layer)
    if "wms_style" in wmsconfig:
        wms_style = wmsconfig["wms_style"]
        logger.debug("Got overriden wms_style: %s", wms_style)
    if "wms_zoom_level" in wmsconfig:
        wms_zoom_level = wmsconfig["wms_zoom_level"]
        logger.debug("Got overriden wms_zoom_level: %s", wms_zoom_level)
    if "wms_timeout" in wmsconfig:
        wms_timeout = wmsconfig["wms_timeout"]
        logger.debug("Got overriden wms_timeout: %s", wms_timeout)
    if "add_coastlines" in wmsconfig:
        add_coastlines = wmsconfig["add_coastlines"]
        logger.debug("Got overriden add_coastlines: %s", add_coastlines)
    if "projection" in wmsconfig:
        projection = wmsconfig["projection"]
        logger.debug("Got overriden projection: %s", projection)
    if "thumbnail_extent" in wmsconfig:
        thumbnail_extent = wmsconfig["thumbnail_extent"]
        logger.debug("Got overriden thumbnail_extent: %s", thumbnail_extent)
    if "wms_layers_mmd" in wmsconfig:
        wms_layers_mmd = wmsconfig["wms_layers_mmd"]
        logger.debug("Got wms_layers_mmd list: %s", wms_layers_mmd)

    # Log some info
    logger.info(f"Got thumb path: {path}")
    logger.info(f"Got wms_url: {wms_url}")
    logger.info(f"Got id: {id}")
    base_path = app.conf.get("THUMB_HOST_BASE_PATH")
    image_path = app.conf.get("LOCAL_IMAGE_PATH")
    full_path = f"{base_path}{image_path}{path}"
    logger.debug(f"Genearating thumb: {full_path}")
    try:
        # Your task code here

        create_wms_thumbnail(
            wms_url,
            full_path,
            wms_layer=wms_layer,
            wms_style=wms_style,
            wms_zoom_level=wms_zoom_level,
            wms_timeout=wms_timeout,
            add_coastlines=add_coastlines,
            projection=projection,
            wms_layers_mmd=wms_layers_mmd,
            thumbnail_extent=thumbnail_extent,
        )
        self.update_state(
            state=states.SUCCESS,
            meta=f"WMS Thumbnail {full_path} generated successfully",
        )
        return {"message": f"WMS Thumbnail {full_path} generated successfully"}
    # except Timeout as e:
    #     raise TimeoutError(f"Could not read wms capability: {str(e)}")

    # except XMLSyntaxError as e:
    #    raise e

    # except ParseError as e:
    #     raise TaskError(f"Could not parse capabilty documnet: {str(e)}")
    # except ServiceException as e:
    #     raise TimeoutError(f"WMS service error: {str(e)}")
    except SoftTimeLimitExceeded:
        try:
            raise self.retry(countdown=60)  # Retry the task in 60 seconds
        except self.MaxRetriesExceededError:
            return "Task failed after maximum retries"
    except Exception as e:
        self.update_state(
            state=states.FAILURE,
            meta={"exc_type": type(e).__name__, "exc_message": str(e)},
        )
        logger.debug("Exception: %s", str(e))

        raise TaskError(str(e)) from e


def create_wms_thumbnail(
    url,
    full_path,
    wms_layer=None,
    wms_style=None,
    wms_zoom_level=0,
    wms_timeout=120,
    add_coastlines=None,
    projection=None,
    wms_layers_mmd=None,
    thumbnail_extent=None,
):
    """Create a base64 encoded thumbnail by means of cartopy.

    Args:
        url: wms GetCapabilities document

    Returns:
        thumbnail_b64: base64 string representation of image
    """
    if wms_layers_mmd is None:
        wms_layers_mmd = []

    logger.debug("%s. Starting wms url %s", mp.current_process().name, url)
    wms_layer = wms_layer
    wms_style = wms_style
    wms_zoom_level = wms_zoom_level
    wms_timeout = wms_timeout
    add_coastlines = add_coastlines
    map_projection = projection
    thumbnail_extent = thumbnail_extent

    # map projection string to ccrs projection
    if isinstance(map_projection, str):
        if map_projection == "PolarStereographic":
            map_projection = ccrs.Stereographic(
                central_longitude=0.0, central_latitude=90.0, true_scale_latitude=60.0
            )
        else:
            map_projection = getattr(ccrs, map_projection)()
    if map_projection is None:
        map_projection = ccrs.PlateCarree()
    logger.debug("Opening wms url %s with timeout %d", url, wms_timeout)

    # Pick the first layer from the mmd layers list
    wms_layer_mmd = None
    if wms_layers_mmd is not None and len(wms_layers_mmd) > 0:
        wms_layer_mmd = wms_layers_mmd[0]

    """Some debugging"""
    logger.debug("wms_layer: %s", wms_layer)
    logger.debug("wms_layer from MMD: %s", wms_layer_mmd)
    logger.debug("wms_style: %s", wms_style)
    logger.debug("wmz_zoom_level: %d", wms_zoom_level)
    logger.debug("add_coastlines: %s", add_coastlines)
    logger.debug("map_projection:  %s", map_projection)
    logger.debug("thumbnail_extent: %s", thumbnail_extent)

    # Check if url is list or string, and process therafter
    if isinstance(url, list):
        url = url[0]  # Extract first url

    # Make sure url does not provide request attributes
    url = url.split("?")[0]

    if url.startswith("http://thredds.nersc"):
        url.replace("http:", "https:")

    if url.startswith("http://nbswms.met.no"):
        url.replace("http:", "https:")

    # Local test
    # url = url.replace('https://fastapi.s-enda-dev.k8s.met.no/', 'http://localhost:8000/')

    # map projection string to ccrs projection
    if isinstance(map_projection, str):
        map_projection = getattr(ccrs, map_projection)()
        logger.debug("map_projection:  %s", map_projection)
    logger.debug("Opening wms url %s with timeout %d", url, wms_timeout)
    wms = None
    try:
        wms = WebMapService(url, version="1.3.0", timeout=int(wms_timeout))
    except Exception as e:
        wms = None
        raise Exception("Could not read wms capability: ", e) from e

    """Some debugging"""
    logger.debug("Title: %s", wms.identification.title)
    logger.debug("Type: %s", wms.identification.type)
    logger.debug("Operations: %s", [op.name for op in wms.operations])
    logger.debug("GetMap options: %s", wms.getOperationByName("GetMap").formatOptions)

    """Get avilable layers and tiles"""
    available_layers = list(wms.contents.keys())
    logger.debug("Available layers :%s", available_layers)

    available_layers_titles = []
    for layer in available_layers:
        available_layers_titles.append(wms.contents[layer].title)
    logger.debug("Available layers titles :%s", available_layers_titles)

    if len(available_layers) == 0:
        raise Exception("No layers found. Cannot create thumbnail.")

    # Handle layer selection
    if wms_layer not in available_layers:
        # Layer from commandline/config not in available layers. Check MMD
        if wms_layer_mmd in available_layers:
            wms_layer = wms_layer_mmd
            logger.debug("Got layer from MMD: %s", wms_layer)
        # Check if MMD layers was given with title instead of name as for NBS
        elif wms_layer_mmd in available_layers_titles:
            idx = available_layers_titles.index(wms_layer_mmd)
            wms_layer = available_layers[idx]
            logger.debug(
                "Matched MMD wms layer title %s, found layer name: %s",
                wms_layer_mmd,
                wms_layer,
            )
        # Fallback. Choose the first from capabilities after removing blacklisted layers
        else:
            with contextlib.suppress(ValueError):
                for layer in blacklist_layers:
                    available_layers.remove(layer)
                wms_layer = available_layers[0]
    logger.debug(f"Creating WMS thumbnail for layer: {wms_layer}")
    # logger.debug("layer: %s", wms_layer)
    # logger.debug("Abstract: ", wms_layer.abstract)
    # logger.debug("BBox: ", wms_layer.boundingBoxWGS84)
    # logger.debug("CRS: ", wms_layer.crsOptions)
    # logger.debug("Styles: ", wms_layer.styles)
    # logger.debug("Timestamps: ", wms_layer.timepositions)

    # Checking styles
    available_styles = list(wms.contents[wms_layer].styles.keys())
    logger.debug(f"Input style: {wms_style}  . Available Styles: {available_styles}")
    if available_styles:
        if wms_style not in available_styles:
            wms_style = [available_styles[0]]
    else:
        wms_style = None

    if wms_style is not None and isinstance(wms_style, str):
        wms_style = [wms_style]
    logger.debug("Selected style: %s", wms_style)

    if not thumbnail_extent:
        wms_extent = wms.contents[wms_layer].boundingBoxWGS84
        logger.debug("Wms extent, %s", wms_extent)
        # cartopy_extent = [wms_extent[0], wms_extent[2],
        #                  wms_extent[1], wms_extent[3]]

        cartopy_extent_zoomed = [
            wms_extent[0] - wms_zoom_level,
            wms_extent[2] + wms_zoom_level,
            wms_extent[1] - wms_zoom_level,
            wms_extent[3] + wms_zoom_level,
        ]
    else:
        cartopy_extent_zoomed = thumbnail_extent

    max_extent = [-180.0, 180.0, -90.0, 90.0]

    for i, extent in enumerate(cartopy_extent_zoomed):
        if i % 2 == 0:
            if extent < max_extent[i]:
                cartopy_extent_zoomed[i] = max_extent[i]
        else:
            if extent > max_extent[i]:
                cartopy_extent_zoomed[i] = max_extent[i]

    subplot_kw = dict(projection=map_projection)
    logger.debug(subplot_kw)

    logger.debug("creating subplot.")
    # lock.acquire()
    fig = None
    try:
        fig, ax = plt.subplots(subplot_kw=subplot_kw)
    except Exception as e:
        if fig is not None:
            plt.close(fig)
        plt.cla()
        fig = None
        ax = None
        wms = None
        plt.close("all")
        raise Exception("Could not plot wms: ", e) from e

    # logger.debug(type(ax))
    # logger.debug(ax)
    # logger.debug(ax.get_extent())
    # land_mask = cartopy.feature.NaturalEarthFeature(category='physical',
    #                                                scale='50m',
    #                                                facecolor='#cccccc',
    #                                                name='land')
    # ax.add_feature(land_mask, zorder=0, edgecolor='#aaaaaa',
    #        linewidth=0.5)

    # transparent background
    ax.spines["geo"].set_visible(False)
    # ax.outline_patch.set_visible(False)
    # ax.background_patch.set_visible(False)
    fig.patch.set_alpha(0)
    fig.set_alpha(0)
    fig.set_figwidth(4.5)
    fig.set_figheight(4.5)
    fig.set_dpi(100)
    # ax.background_patch.set_alpha(1)
    logger.debug("ax.add_wms(layer=%s, style=%s).", wms_layer, wms_style)
    ax.add_wms(
        wms, layers=[wms_layer], wms_kwargs={"transparent": False, "styles": wms_style}
    )

    if add_coastlines:
        ax.coastlines(resolution="50m", linewidth=0.5)
    if map_projection == ccrs.PlateCarree():
        ax.set_extent(cartopy_extent_zoomed)
    else:
        ax.set_extent(cartopy_extent_zoomed, ccrs.PlateCarree())

    # Check and create directories if not existing
    # Split the file path into directory and filename components
    logger.debug("Full image_path: %s", full_path)
    directory, filename = os.path.split(full_path)
    create_directories(directory)

    fig.savefig(full_path, format="png", bbox_inches="tight")
    plt.close(fig)
    plt.cla()
    plt.close("all")
    del fig
    del ax
    del wms
    logger.debug("%s. Finished", mp.current_process().name)
    return


def create_directories(path):
    """Create path if it not exsists"""
    if not os.path.exists(path):
        os.makedirs(path)
