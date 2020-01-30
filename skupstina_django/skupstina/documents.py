from elasticsearch_dsl import analyzer, tokenizer
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Act, Subject, Item, Period

act_analyzer = analyzer(
    'act_analyzer',
    tokenizer=tokenizer('standard'),
    filter=['lowercase', 'snowball']
)


@registry.register_document
class ActDocument(Document):
    subject = fields.ObjectField(
        properties={
            'subject_title': fields.TextField(),
            'subject_url': fields.TextField(),
            'item': fields.ObjectField(
                properties={
                    'item_title': fields.TextField(),
                    'item_number': fields.IntegerField(),
                    'item_text': fields.TextField(),
                    'period': fields.ObjectField(
                        properties={
                            'period_text': fields.TextField(),
                            'start_date': fields.DateField(),
                            'end_date': fields.DateField(),
                            'parent_url': fields.TextField(),
                            'period_url': fields.TextField(),
                        }
                    )
                }
            )
        }
    )

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
            'title',
            'content_url',
        ]
        related_models = [Subject, Item, Period]  # Optional: to ensure the Act will be re-saved when Subject is updated

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(ActDocument, self).get_queryset().select_related(
            'subject', 'subject__item', 'subject__item__period',
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Subject):
            return related_instance.act_set.all()

