from django.db import models
import uuid

class Movies(models.Model):
    title = models.CharField(default='',max_length=300)
    description = models.TextField(default='')
    genres = models.CharField(default='',max_length=300)
    uuid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.title


class MoviesCollection(models.Model):
    title = models.CharField(default='',max_length=300)
    description = models.TextField(default='')
    movies = models.ManyToManyField(Movies, related_name='collections')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return self.title

class RequestCount(models.Model):
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"Request Count:{self.count}"
