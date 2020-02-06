# Generated by Django 3.0.2 on 2020-02-03 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScraperPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_text', models.CharField(max_length=100, unique=True)),
                ('scrape_completed', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('year_range', models.CharField(choices=[('2017-20xx', '2017-20xx'), ('2013-2017', '2013-2017'), ('2009-2013', '2009-2013')], max_length=20)),
            ],
        ),
    ]