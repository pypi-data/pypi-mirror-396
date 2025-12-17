from django.db import models


class TaskReconstruction(models.Model):
    task_id = models.CharField(max_length=255, primary_key=True)
    task_name = models.CharField(max_length=255)
    task_args = models.TextField()
    task_kwargs = models.TextField()
    queue_options = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'taskqueue_task_reconstruction'
        app_label = 'taskqueue'

    def __str__(self):
        return f"TaskReconstruction({self.task_id})"
