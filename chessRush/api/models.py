from django.db import models

# Create your models here.
class ChessPuzzle(models.Model):
    fen = models.TextField()
    moves = models.TextField()
    theme = models.TextField(default='')
    url = models.URLField()
    opening_fam = models.TextField()
    opening_variation = models.TextField()

class AutomateFen(models.Model):
    fen = models.CharField(max_length=40, unique=True)
    win = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    loose = models.IntegerField(default=0)
    count = models.IntegerField(default=1)
