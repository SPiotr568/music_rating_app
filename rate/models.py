from django.db import models

from django.contrib.auth.models import User


class Reviewer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.name)


class Song(models.Model):
    name = models.CharField(max_length=100, null=True)
    author = models.CharField(max_length=100, null=True)
    url = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    reviewers = models.ManyToManyField(Reviewer, through='Rating')
    overall_rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)


class Rating(models.Model):
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    rate = models.FloatField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.rate)
