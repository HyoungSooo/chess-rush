from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
import random
from django.db.models import *
from django.conf import settings
from .models import ChessPuzzle, AutomateFen
from django.urls import path,include
from .utils import write_pgn_chunk_files, get_stockfish, create_random_fen
from .processor import PuzzleProcess
from django.views.generic import TemplateView
from collections import defaultdict
from django.db import transaction

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
            pk=pk).filter(theme__icontains = 'underPromotion').values('fen', 'moves').first()
        if puzzle:
            return JsonResponse(puzzle, safe=False)

ONE_DAY = 60*60*24

class UserInterface(Schema):
    username:str
    region:str
    score:int
@transaction.atomic
@api.post('/rank')
def get_client_ip(request, data:UserInterface):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    total = cache.get('total')

    if total == None:
       total = 1
    else:
        total += 1
    
    cache.set('total', total, ONE_DAY*365)

    rank = cache.get('rank')
    if rank == None:
        rank = {ip : {'username' : data.username, 'region': data.region, 'score': data.score}}
    else:
        rank[ip] = {'username' : data.username, 'region': data.region, 'score': data.score}
    
    cache.set('rank', rank, 60*60*24)
    
    return JsonResponse(rank,safe=False)

@api.get('/rank')
def get_rank(request):
    try:
      return sorted(cache.get('rank').values(), key=lambda x: x['score'], reverse=True)
    except:
      return []


@api.post('/cache')
def clear_all_cache(request, key:ApiKey):
    
    if key.apikey != 'apikey':
        return False

    total_played = cache.get('total')

    if total_played == None:
        total_played = 0

    cache.clear()
    cache.set('total',total_played, ONE_DAY*365)

@api.get('total')
def get_total_palyed_game(request):
    return cache.get('total')

@api.get('/stockfish')
def stockfish_recommend(request, fen: str):
    stockfish = get_stockfish()
    stockfish.set_fen_position(fen)
    return stockfish.get_best_move()
      

@api.get('fen')
def get_random_fen(request):
    max_id = AutomateFen.objects.all().aggregate(max_id=Max("id"))['max_id']
    if max_id == None:
        fen_list = create_random_fen(100)
        create_list = []
        for i in fen_list:
            create_list.append(AutomateFen(fen = i))
        
        AutomateFen.objects.bulk_create(create_list)
            
    while True:
        pk = random.randint(1, max_id)
        fen = AutomateFen.objects.filter(
            pk=pk).values('fen').first()
        if fen:
            return JsonResponse(fen, safe=False)

    
urlpatterns = [
    path('', api.urls),
    path('sample/', TemplateView.as_view(template_name='puzzle_attack.html'), name='puzzle'),
    path('sample/automate', TemplateView.as_view(template_name='automate.html'), name='puzzle'),
]
