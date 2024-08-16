
from django.db import models

class Message(models.Model):
    name = models.CharField(max_length=255, unique=True)
    text = models.TextField()

    def __str__(self):
        return self.name
