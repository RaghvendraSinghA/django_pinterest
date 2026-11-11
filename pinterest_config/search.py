from .elasticsearch import es
import logging
logger = logging.getLogger(__name__)


def fuzzy_search_pins(query):
    try:
        response = es.search(
            index="pins",
            query={
                "multi_match": {
                    "query": query,
                    "fields": ["title", "description"],
                    "fuzziness": "AUTO"
                }
            }
        )

        return response["hits"]["hits"]

    except Exception:
        logger.exception(
            "Elasticsearch search failed for query: %s",
            query
        )
        raise