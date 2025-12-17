from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TaskReconstruction',
            fields=[
                ('task_id', models.CharField(
                    max_length=255, primary_key=True, serialize=False)),
                ('task_name', models.CharField(max_length=255)),
                ('task_args', models.TextField()),
                ('task_kwargs', models.TextField()),
                ('queue_options', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'taskqueue_task_reconstruction',
            },
        ),
    ]
