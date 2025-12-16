import geodesic


def get_linkml(dataset: geodesic.Dataset, collection: str) -> str:
    """Get the LinkML schema for the dataset."""
    if not isinstance(dataset, geodesic.Dataset):
        raise TypeError("Expected a geodesic.Dataset instance.")
    client = dataset._servicer_client("alpha")
    url = f"/mappings/v1/linkml/{collection}"
    resp = client.get(url)
    resp = geodesic.raise_on_error(resp)
    return resp.text


def write_linkml(
    dataset: geodesic.Dataset,
    collection: str,
    filename: str = None,
) -> None:
    """Write the LinkML schema for this collection of the dataset as a local YAML file."""
    if not isinstance(dataset, geodesic.Dataset):
        raise TypeError("Expected a geodesic.Dataset instance.")
    linkml = get_linkml(dataset, collection)
    if filename is None:
        filename = f"{collection}.linkml.yaml"
    elif not filename.endswith(".yaml"):
        filename += ".yaml"
    if not filename.startswith("/"):
        filename = f"./{filename}"
    with open(filename, "w") as f:
        f.write(linkml)
