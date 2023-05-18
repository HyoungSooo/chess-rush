from django.db import models

# Create your models here.
class ChessPuzzle(models.Model):
    fen = models.TextField()
    moves = models.TextField()
    theme = models.TextField(default='')
    url = models.URLField()
    opening_fam = models.TextField()
    opening_variation = models.TextField()