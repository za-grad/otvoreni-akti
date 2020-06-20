from django.db import models


class ScraperPeriod(models.Model):
    date = models.DateTimeField()
    scrape_completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.date)
