from .elasticsearch import es
from pin_app.models import Pin
from elasticsearch.helpers import bulk


def create_pins_index():
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