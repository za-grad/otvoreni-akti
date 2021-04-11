from django.db import models


class ScraperPeriod(models.Model):
    url = models.CharField(max_length=300, unique=True)
    date = models.DateTimeField()
    period_text = models.CharField(max_length=100, null=True)
    scrape_completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.url)
