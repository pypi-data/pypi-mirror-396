import functools

from geodesic.config import SearchReturnType
from geodesic.client import get_requests_client, raise_on_error
from geodesic.entanglement.graph import Graph

import rdflib
from requests import Response


def search_decorator(search, **kwargs):
    @functools.wraps(search)
    def wrapper(
        self,
        **kwargs,
    ):
        return_type = kwargs.get("return_type", None)
        if return_type == SearchReturnType.RDFLIB_GRAPH:
            limit, page_size, many_records = self._limit_and_page_size(
                kwargs.get("limit", 10),
                kwargs.get("page_size", None),
                kwargs.get("ids", None),
            )

            # Force Turtle format for RDF results
            kwargs["extra_post_params"] = kwargs.get("extra_post_params", {})
            kwargs["extra_post_params"]["format"] = "ttl"
            kwargs.pop("limit", None)
            kwargs.pop("page_size", None)

            search_res = self._run_search(page_size=page_size, **kwargs)

            if many_records:
                return _page_through_rdf_results(search_res, page_size, limit)
            graph = rdflib.Graph()
            graph.parse(data=search_res.text, format="ttl")
            return graph
        else:
            return search(self, **kwargs)

    return wrapper


def _page_through_rdf_results(res: Response, page_size: int, limit: int = None) -> "Graph":
    next_link = res.headers.get("Boson-Next-Page-Link")
    total_processed_rows = int(res.headers.get("Boson-Processed-Rows", 0))

    graph = rdflib.Graph()
    graph.parse(data=res.text)

    if limit and total_processed_rows >= limit:
        return graph

    while next_link:
        remaining = page_size
        if limit - total_processed_rows < page_size:
            remaining = limit - total_processed_rows
        res = raise_on_error(
            get_requests_client().get(
                next_link, headers={"Boson-Requested-Remaining-Rows": str(remaining)}
            )
        )
        next_link = res.headers.get("Boson-Next-Page-Link")
        total_processed_rows += int(res.headers.get("Boson-Processed-Rows", 0))
        try:
            graph.parse(data=res.text)
        except Exception as e:
            raise e
        if limit and total_processed_rows >= limit:
            break

    return graph
