import geodesic
from geodesic.client import raise_on_error


def add_ontology(dataset: geodesic.Dataset, ontology_path: str) -> dict:
    client = dataset._servicer_client("alpha")
    url = "/mappings/v1/ontologies"

    with open(ontology_path, "r") as f:
        ontology = f.read()

    resp = client.post(
        url,
        data=ontology,
    )

    resp = raise_on_error(resp)
    return resp.json()
