from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TaskReconstruction',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_result', models.OneToOneField(
                    on_delete=models.deletion.CASCADE,
                    to='django_celery_results.taskresult',
                )),
                ('task_id', models.CharField(
                    db_index=True, max_length=255, unique=True)),
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
