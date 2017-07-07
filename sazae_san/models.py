from django.db import models

class Episode(models.Model):
    HANDS = [("グー", "グー"), ("チョキ", "チョキ"), ("パー", "パー")]
    air_time = models.DateField()
    hand = models.CharField(max_length = 3, choices = HANDS)