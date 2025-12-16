from __future__ import annotations
from prettytable import PrettyTable, MARKDOWN


def _create_table(field_names, align_left=True, style=None):
    """Create a PrettyTable with standard configuration."""
    table = PrettyTable()
    table.field_names = field_names
    if align_left:
        for field in field_names:
            table.align[field] = "l"
    if style:
        table.set_style(style)
    return table


def _fix_html_alignment(html):
    """Fix HTML table alignment to left."""
    return html.replace(
        'th style="padding-left: 1em; padding-right: 1em; text-align: center"',
        'th style="padding-left: 1em; padding-right: 1em; text-align: left"',
    )


def _extract_asset_bands(asset_band):
    """Extract asset and bands from dict or object."""
    if isinstance(asset_band, dict):
        return asset_band.get("asset", ""), asset_band.get("bands", [])
    else:
        return getattr(asset_band, "asset", ""), getattr(asset_band, "bands", [])


def _format_spatial_bbox(spatial):
    """Format spatial bbox for display, returns list of (label, bbox_str) tuples."""
    rows = []
    if not spatial:
        return rows

    bbox = spatial.get("bbox")
    if not bbox:
        return rows

    if isinstance(bbox[0], list):
        for i, b in enumerate(bbox, 1):
            bbox_str = ", ".join(str(coord) for coord in b)
            label = f"bbox {i}" if len(bbox) > 1 else "bbox"
            rows.append(("spatial", label, bbox_str))
    else:
        bbox_str = ", ".join(str(coord) for coord in bbox)
        rows.append(("spatial", "bbox", bbox_str))

    return rows


def _format_temporal_interval(temporal):
    """Format temporal interval for display, returns list of (label, interval_str) tuples."""
    rows = []
    if not temporal:
        return rows

    interval = temporal.get("interval")
    if not interval:
        return rows

    if isinstance(interval[0], list):
        for i, intv in enumerate(interval, 1):
            start = intv[0] if intv[0] else "None"
            end = intv[1] if intv[1] else "None"
            interval_str = f"{start}, {end}"
            label = f"interval {i}" if len(interval) > 1 else "interval"
            rows.append(("temporal", label, interval_str))
    else:
        start = interval[0] if interval[0] else "None"
        end = interval[1] if interval[1] else "None"
        interval_str = f"{start}, {end}"
        rows.append(("temporal", "interval", interval_str))

    return rows


def _convert_geometry_types_to_rows(geometry_dict):
    """Convert geometry types dict to list of dicts with Collection/Geometry Type/Count columns."""
    if not geometry_dict or not isinstance(geometry_dict, dict):
        return []

    dict_list = []
    try:
        for collection_name, geom_type in geometry_dict.items():
            if isinstance(geom_type, dict):
                # Handle dict format: {"Point": 100, "Polygon": 50}
                for geom, count in geom_type.items():
                    dict_list.append(
                        {"Collection": collection_name, "Geometry Type": geom, "Count": str(count)}
                    )
            elif isinstance(geom_type, (list, tuple)):
                # Handle list format: ["Point", "Polygon", "LineString"]
                for geom in geom_type:
                    dict_list.append(
                        {"Collection": collection_name, "Geometry Type": geom, "Count": ""}
                    )
            else:
                # Fallback for other types
                dict_list.append(
                    {"Collection": collection_name, "Geometry Type": str(geom_type), "Count": ""}
                )
    except (AttributeError, TypeError):
        return []
    return dict_list


def _convert_raster_assets_to_rows(assets_dict):
    """Convert raster assets dict to list of dicts with Asset/Band columns."""
    if not assets_dict or not isinstance(assets_dict, dict):
        return []

    dict_list = []
    try:
        for asset_name, asset_info in assets_dict.items():
            bands = asset_info.get("bands", []) if isinstance(asset_info, dict) else []
            if bands:
                for band in bands:
                    dict_list.append({"Asset": asset_name, "Band": str(band)})
            else:
                # Add a row with empty band if no bands defined
                dict_list.append({"Asset": asset_name, "Band": ""})
    except (AttributeError, TypeError):
        return []
    return dict_list


def _convert_extent_to_rows(extent_dict):
    """Convert extent dict to list of dicts with Extent/Type/Value columns."""
    if not extent_dict or not isinstance(extent_dict, dict):
        return []

    dict_list = []

    try:
        # Process spatial extent
        for row in _format_spatial_bbox(extent_dict.get("spatial")):
            extent, type_label, value = row
            dict_list.append({"Extent": extent, "Type": type_label, "Value": value})

        # Process temporal extent
        for row in _format_temporal_interval(extent_dict.get("temporal")):
            extent, type_label, value = row
            dict_list.append({"Extent": extent, "Type": type_label, "Value": value})
    except (AttributeError, TypeError):
        return []

    return dict_list


def _convert_asset_bands_to_rows(bands_list):
    """Convert list of asset band objects to list of dicts with Asset/Bands columns."""
    if not bands_list or not isinstance(bands_list, (list, tuple)):
        return []

    dict_list = []
    try:
        for ab in bands_list:
            asset, bands = _extract_asset_bands(ab)
            bands_str = ", ".join(str(b) for b in bands) if bands else ""
            dict_list.append({"Asset": asset, "Bands": bands_str})
    except (AttributeError, TypeError):
        return []
    return dict_list


def render_table_str(headers, rows):
    """Generic markdown table renderer from headers and list of dict rows."""
    if not rows:
        return None
    table = _create_table(headers, align_left=True, style=MARKDOWN)
    for row in rows:
        table.add_row([row.get(h, "") for h in headers])
    return str(table)


def render_table_html(headers, rows):
    """Generic HTML table renderer from headers and list of dict rows."""
    if not rows:
        return None
    table = _create_table(headers)
    for row in rows:
        table.add_row([row.get(h, "") for h in headers])
    return _fix_html_alignment(table.get_html_string(format=True))


def render_properties_table_str(obj_dict, title=None):
    """Generic 'Property | Value' table for string display."""
    if not obj_dict:
        return f"{title or 'Object'}(empty)"

    table = _create_table(["Property", "Value"], align_left=True, style=MARKDOWN)
    for key, value in obj_dict.items():
        if value is not None:
            property_name = key.replace("_", " ").title()
            table.add_row([property_name, str(value)])
    return str(table)


def render_properties_table_html(obj_dict, title=None):
    """Generic 'Property | Value' table for HTML display."""
    if not obj_dict:
        return f"<p>{title or 'Object'}(empty)</p>"

    table = _create_table(["Property", "Value"])
    for key, value in obj_dict.items():
        if value is not None:
            property_name = key.replace("_", " ").title()
            table.add_row([property_name, str(value)])

    html = "<div style='margin: 10px;'>"
    if title:
        html += f"<h3>{title}</h3>"
    html += _fix_html_alignment(table.get_html_string(format=True))
    html += "</div>"
    return html


def format_grouped_data(data_dict, headers, value_accessor):
    """Generic formatter for grouped data (e.g., queryables grouped by collection).

    Args:
        data_dict: dict like {group_name: {item_name: item_info}}
        headers: list of column headers
        value_accessor: function(item_name, item_info) -> dict with header keys

    Returns: formatted markdown string
    """
    if not data_dict:
        return None

    output_parts = []
    for group_name, items in data_dict.items():
        if not items:
            continue
        output_parts.append(f"**{group_name}:**")
        rows = []
        for name, info in items.items():
            row = value_accessor(name, info)
            rows.append(row)
        table_str = render_table_str(headers, rows)
        if table_str:
            output_parts.append(table_str)

    return "\n".join(output_parts) if output_parts else None


def format_grouped_data_html(data_dict, headers, value_accessor, section_tag="h4"):
    """Generic HTML formatter for grouped data.

    Args:
        data_dict: dict like {group_name: {item_name: item_info}}
        headers: list of column headers
        value_accessor: function(item_name, item_info) -> dict with header keys
        section_tag: HTML tag for group headers

    Returns: HTML string
    """
    if not data_dict:
        return None

    html_parts = []
    for group_name, items in data_dict.items():
        if not items:
            continue
        html_parts.append(f"<{section_tag}>{group_name}</{section_tag}>")
        rows = []
        for name, info in items.items():
            row = value_accessor(name, info)
            rows.append(row)
        table_html = render_table_html(headers, rows)
        if table_html:
            html_parts.append(table_html)

    return "\n".join(html_parts) if html_parts else None
