from django.db import models


class Event(models.Model):
    eventName = models.CharField(max_length=32)
    description = models.TextField()
    location = models.CharField(max_length=32)
    fromDate = models.DateField()
    fromTime = models.TimeField()
    toDate = models.DateField()
    toTime = models.TimeField()
    deadlineDate = models.DateField()
    deadlineTime = models.TimeField()
    email = models.EmailField()
    password = models.CharField(max_length=32)

    def __str__(self):
        return self.eventName


class Participant(models.Model):
    name = models.CharField(max_length=32)
    cno = models.IntegerField()
    email = models.EmailField()
    event = models.CharField(max_length=32)
    regType = models.CharField(max_length=32)
    groupSize = models.IntegerField()

    def __str__(self):
        return self.name

