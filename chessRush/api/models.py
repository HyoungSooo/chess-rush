from django.db import models

# Create your models here.
class ChessPuzzleTheme(models.Model):
    theme = models.CharField(max_length=10)

class ChessPuzzle(models.Model):
    theme = models.ForeignKey(ChessPuzzleTheme, on_delete=models.CASCADE,related_name='puzzle')
    fen = models.TextField()
    moves = models.TextField()
    url = models.URLField()
    opening_fam = models.TextField()
    opening_variation = models.TextField()

class AutomateFen(models.Model):
    name = models.CharField(max_length=10)
    fen = models.CharField(max_length=40, unique=True)
    win = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    loose = models.IntegerField(default=0)
    count = models.IntegerField(default=1)
