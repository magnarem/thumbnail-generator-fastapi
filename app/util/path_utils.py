from urllib.parse import urlparse

from app.models.thumbnail_request import WMSThumbRequest


def generate_thumbnail_paths(
    request: WMSThumbRequest, thumb_host: str, image_path: str
) -> tuple[str, str]:
    """
    Generate internal file path and full URL for a thumbnail based on the request and config.
    Path format: <naming_authority_or_reversed_host>/<date_path_or_fallback>/<id>.png
    """
    wms_url = str(request.wms_url)
    # Remove query parameters from url
    if "?" in wms_url:
        wms_url = wms_url.split("?", maxsplit=1)[0]

    identifier = request.id
    # Check for naming authority in identifier (e.g., 'authority:restofid')
    if ":" in identifier:
        naming_authority, local_id = identifier.split(":", 1)
        base_dir = naming_authority
        filename = local_id
    else:
        local_id = identifier
        parsed_url = urlparse(wms_url)
        host = parsed_url.hostname or ""
        base_dir = ".".join(reversed(host.split("."))) if host else "unknown"
        filename = local_id

    # Get date or fallback (shard only from local_id)
    if request.start_date:
        dt = request.start_date.date()
        date_path = dt.strftime("%Y/%m/%d")
    else:
        date_path = local_id[:4] if len(local_id) >= 4 else "no_date"

    # Build path
    path = f"{base_dir}/{date_path}/{filename}.png"
    full_path = f"{thumb_host}{image_path}{path}"
    return path, full_path
