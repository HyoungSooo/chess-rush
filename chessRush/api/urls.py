from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
import random
from django.db.models import *
from django.conf import settings
from .models import ChessPuzzle, AutomateFen, ChessPuzzleTheme
from django.urls import path,include
from .utils import write_pgn_chunk_files, get_stockfish, create_random_fen
from .processor import PuzzleProcess
from django.views.generic import TemplateView
from collections import defaultdict
from django.db import transaction
from django.core import serializers

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
def get_random_puzzle(request, score:int):
    
    if 0 <= score < 5:
        theme = 'mateIn1'
    elif 5 <= score < 10:
        theme = 'short'
    elif 10 <= score < 25:
        theme = 'long'
    else:
        theme = 'veryLong'
    return ChessPuzzleTheme.objects.get(theme = theme).puzzle.all().order_by("?").values('fen', 'moves').first()

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
        try:
          rank[ip] = max({'username' : data.username, 'region': data.region, 'score': data.score}, rank[ip], key= lambda x: x['score'])
        except:
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

@api.get('/total')
def get_total_palyed_game(request):
    return cache.get('total')

@api.get('/stockfish')
def stockfish_recommend(request, fen: str):
    stockfish = get_stockfish()
    stockfish.set_fen_position(fen)
    return stockfish.get_best_move()
      

@api.get('/fen')
def get_random_fen(request):
    max_id = AutomateFen.objects.all().aggregate(max_id=Max("id"))['max_id']
    if max_id == None:
        fen_list = create_random_fen(20)
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
        
class Fen(Schema):
    fen:str
    color:bool = None
        
@api.post('/fen')
def create_fen(request, fen:Fen):
    data = fen.fen.split('/')
    data = '/'.join(data[4:])[::-1].lower() + '/'
    data = AutomateFen.objects.get_or_create(fen=data)
    if not data[1]:
        data[0].count += 1
        data[0].save()
    
    return data[0].fen
        

@api.get('/fen/list')
def get_fen_list_20_order_by_win_rate(request):
    data = list(AutomateFen.objects.all().order_by('-win').values('fen','win')[:20])
    return JsonResponse(data, safe=False)

@api.post('/fen/rate')
def increase_win_count_of_fen(request,fen:Fen):
    if fen.color == 'None':
        return
    
    if fen.color:
        data = fen.fen.split('/')
        data = '/'.join(data[4:])[::-1].lower() + '/'
    else:
        data = '/'.join(fen.fen.split('/')[:4]) + '/'

    with transaction.atomic():
      fen = AutomateFen.objects.select_for_update().get(fen=data)
      fen.win += 1
      fen.save()

      return


    
urlpatterns = [
    path('', api.urls),
    path('rush/', TemplateView.as_view(template_name='puzzle_attack.html'), name='puzzle'),
    path('automate', TemplateView.as_view(template_name='automate.html'), name='automate'),
    path('index/', TemplateView.as_view(template_name='index.html')),
]
