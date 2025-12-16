import geodesic
from geodesic.bases import _APIObject
from geodesic.descriptors import (
    _ListDescr,
    _StringDescr,
    _DictDescr,
    _TypeConstrainedDescr,
    _BoolDescr,
)
from geodesic.client import raise_on_error


class SKOSTriple(_APIObject):
    """A SkoSTriple is a mapping between a geodesic.Object and a geodesic.Dataset."""

    subject = _TypeConstrainedDescr((geodesic.Object, dict, str))
    predicate = _StringDescr(
        one_of=[
            "exactMatch",
            "closeMatch",
            "relatedMatch",
            "broadMatch",
            "narrowMatch",
            "skos:exactMatch",
            "skos:closeMatch",
            "skos:relatedMatch",
            "skos:broadMatch",
            "skos:narrowMatch",
        ]
    )
    object = _StringDescr()
    object_is_literal = _BoolDescr(
        default=False,
        doc="apply this mapping to the column's IRI, not its value. If this is False, the mapping "
        "will promote the literal value to an IRI for each unique value. This property is "
        "ignored for datatype properties.",
    )
    label_column = _StringDescr(
        default=None, doc="The column to use for rdfs:label for a mapped row."
    )
    description_column = _StringDescr(
        default=None, doc="The column to use for rdfs:comment for a mapped row."
    )
    bands = _ListDescr(
        item_type=str,
        default=[],
        doc="For asset mappings, the list of bands that this mapping applies to. If empty or None"
        "this mapping applies to the asset as a whole.",
    )


class Mapping(_APIObject):
    collection_id = _StringDescr(doc="the collection ID to apply this mapping to")
    objects = _ListDescr(
        item_type=(geodesic.Object, dict),
        coerce_items=True,
        doc="a list of entanglement objects that will be connected to this dataset and referenced "
        "in the mapping",
    )
    rows = _ListDescr(item_type=(SKOSTriple, dict), coerce_items=True, doc="a list of row mappings")
    columns = _DictDescr(doc="a dict of column name to list of SKOSTriple mappings")
    assets = _DictDescr(doc="a dict of asset name to list of SKOSTriple mappings")

    dataset = _TypeConstrainedDescr(geodesic.Dataset)

    def delete(self):
        """Delete this mapping from the dataset."""
        client = self.dataset._servicer_client("alpha")
        url = f"/mappings/v1/mappings/{self.collection_id}"

        resp = client.delete(url)
        resp = raise_on_error(resp)
        return resp.json()


def apply_mapping(dataset: geodesic.Dataset, collection: str, mapping: Mapping):
    client = dataset._servicer_client("alpha")
    url = f"/mappings/v1/mappings/{collection}"

    resp = client.post(
        url,
        json=mapping,
    )

    resp = raise_on_error(resp)
    return resp.json()


def get_mapping(dataset: geodesic.Dataset, collection: str) -> Mapping:
    client = dataset._servicer_client("alpha")
    url = f"/mappings/v1/mappings/{collection}"

    resp = client.get(url)
    resp = raise_on_error(resp)
    return Mapping(dataset=dataset, **resp.json())


def list_mappings(dataset: geodesic.Dataset) -> dict:
    client = dataset._servicer_client("alpha")
    url = "/mappings/v1/mappings"

    resp = client.get(url)
    resp = raise_on_error(resp)
    return {
        "mappings": {
            collection_id: Mapping(dataset=dataset, **item)
            for collection_id, item in resp.json().get("mappings", {}).items()
        },
    }
