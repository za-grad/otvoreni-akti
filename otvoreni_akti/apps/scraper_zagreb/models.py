from django.db import models


class ScraperPeriod(models.Model):
    RANGE_CHOICES = [
        ('2017-20xx', '2017-20xx'),
        ('2013-2017', '2013-2017'),
        ('2009-2013', '2009-2013'),
    ]

    period_text = models.CharField(max_length=100, unique=True)
    scrape_completed = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    year_range = models.CharField(
        max_length=20,
        choices=RANGE_CHOICES,
    )

    def __str__(self):
        return self.period_text
