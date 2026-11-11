from .elasticsearch import es


def fuzzy_search_pins(query):
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