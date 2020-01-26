from elasticsearch_dsl import analyzer, tokenizer
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Act


act_analyzer = analyzer(
    'act_analyzer',
    tokenizer=tokenizer('standard'),
    filter=['lowercase', 'snowball']
    )


@registry.register_document
class ActDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'acts'
        # See Elasticsearch Indices API reference for available settings
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    content = fields.TextField(
        analyzer=act_analyzer,
    )

    class Django:
        model = Act
        fields = [
            'act_number',
            'type',
            'subject',
            'content_url',
        ]

