from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=50)
    complete = models.BooleanField(default=False)
    description = models.TextField(max_length=300, null=True, blank=True)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    date_of_updation = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Completed" if self.complete else "Incomplete"
        return f"{self.title} ({status})"

    class Meta:
        ordering = ['-date_of_creation']
