from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from django.http import JsonResponse, HttpResponse
from django.core import serializers
import chess
import random
from django.db.models import *
from django.conf import settings
from .models import ChessPuzzle
from django.urls import path,include
from .utils import write_pgn_chunk_files
from .processor import PuzzleProcess
from django.views.generic import TemplateView

api = NinjaAPI()


@api.post("/upload")
def upload(request, file: UploadedFile = File(...)):
    data = file.read()
    write_pgn_chunk_files(data, file.name)
    return {'name': file.name, 'len': len(data)}

class ApiKey(Schema):
    apikey:str

@api.post('upload/file/puzzle')
def parse_puzzle(request,key:ApiKey):
    if key.apikey == 'apikey':
        PuzzleProcess().puzzle_run()

    return ChessPuzzle.objects.count()
    

@api.get('/puzzle')
def get_random_puzzle(request):
    max_id = ChessPuzzle.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        puzzle = ChessPuzzle.objects.filter(
            pk=pk).values('fen', 'moves').first()
        if puzzle:
            return JsonResponse(puzzle, safe=False)

    
    

urlpatterns = [
    path('', api.urls),
    path('sample/', TemplateView.as_view(template_name='puzzle_attack.html'), name='puzzle'),
]
