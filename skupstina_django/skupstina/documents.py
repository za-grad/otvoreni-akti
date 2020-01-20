from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Act


@registry.register_document
class ActDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'acts'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Act
        fields = [
            'act_number',
            'type',
            'subject',
            'content',
            'content_url',
        ]
