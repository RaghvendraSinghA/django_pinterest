from .elasticsearch import es
from pin_app.models import Pin
from elasticsearch.helpers import bulk


def create_pins_index():

    # This function creates an index named pins in Elasticsearch, with a predefined mapping (schema) describing how Elasticsearch should store and search the fields. It only creates the index structure.

    index_name = "pins"

    if es.indices.exists(index=index_name):
        return "Pins index already exists"

    es.indices.create(
        index=index_name,
        mappings={
            "properties": {
                "id": {"type": "integer"},
                "title": {"type": "text"},
                "description": {"type": "text"}
            }
        }
    )

    return "Pins index created successfully"





def index_existing_pins():
    pins = Pin.objects.all().iterator()
    # iterator make pins as streamable object, so when for-loop is about to complete 1 batch then django will load again new batch of pins from database, in this way we will not load all pins at once and fill the memory.

    actions = [
        {
            "_index": "pins",
            "_id": pin.id,
            "_source": {
                "id": pin.id,
                "title": pin.title,
                "description": pin.description
            }
        }
        for pin in pins
    ]

    success, failed = bulk(es, actions)

    return {
        "indexed": success,
        "failed": failed
    }