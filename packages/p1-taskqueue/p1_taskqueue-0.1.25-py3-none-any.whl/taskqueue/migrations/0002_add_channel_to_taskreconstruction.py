from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('taskqueue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskreconstruction',
            name='channel',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
