from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from django.http import JsonResponse, HttpResponse
from django.core import serializers
import chess
from django.conf import settings
from .models import ChessPuzzle
from django.urls import path,include
from .utils import write_pgn_chunk_files
from .processor import PuzzleProcess

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
    
    
    
    

urlpatterns = [
    path('', api.urls),
]
