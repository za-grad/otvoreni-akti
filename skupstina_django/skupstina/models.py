from django.db import models


class Category(models.Model):
    type = models.CharField(max_length=32, unique=True)


class Source(models.Model):
    category = models.ForeignKey(Category, related_name='type_id', null=True, on_delete=models.CASCADE)
    nr = models.IntegerField()
    year = models.IntegerField()
    week = models.IntegerField()
    date = models.DateTimeField()
    url = models.CharField(max_length=300)


class Item(models.Model):
    source = models.ForeignKey(Source, null=True, on_delete=models.CASCADE)
    item_number = models.IntegerField()
    item_description = models.CharField(max_length=1000)
    subject = models.CharField(max_length=1000)
    unit = models.CharField(max_length=300)
    item_url = models.CharField(max_length=300)


class Act(models.Model):
    item = models.ForeignKey(Item, null=True, on_delete=models.CASCADE)
    act_number = models.IntegerField(null=True)
    type = models.CharField(max_length=32)
    subject = models.CharField(max_length=1000)
    content_url = models.CharField(max_length=1000, unique=True)
    content = models.TextField()
