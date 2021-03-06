from datetime import datetime, timedelta

from django.db import models
from django.contrib.postgres.fields import ArrayField


class Playlist(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    image = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Track(models.Model):
    name = models.CharField(max_length=200)
    popularity = models.PositiveSmallIntegerField()
    duration = models.PositiveIntegerField()
    artists = models.CharField(max_length=200)
    album_name = models.CharField(max_length=200)
    album_image = models.CharField(max_length=200)
    playlists = models.ManyToManyField(Playlist)

    @property
    def duration_formatted(self):
        parsed_duration = datetime.fromtimestamp(self.duration/1000)
        minutes = parsed_duration.minute
        seconds = f"0{parsed_duration.second}" if parsed_duration.second / 10 < 1 else parsed_duration.second
        
        return f"{minutes}:{seconds}"

    def __str__(self):
        return self.name

class TouristAttraction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    selected = models.BooleanField(default=False)
    origin = models.BooleanField(default=False)
    destination = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Graph(models.Model):
    image = models.ImageField(upload_to ='graphs/', null=True)
    origin = models.CharField(max_length=100, default='')
    destination = models.CharField(max_length=100, default='')
    nodes = ArrayField(models.CharField(max_length=100), default=list)
    path = ArrayField(models.CharField(max_length=100), default=list)
    duration = models.FloatField(default=0)

    @property
    def duration_formatted(self):
        minutes_str = str(timedelta(seconds=self.duration)).split(':', 1)[1]
        return minutes_str[:5]
