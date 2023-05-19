from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.core.cache import cache
import random
from django.db.models import *
from django.conf import settings
from .models import ChessPuzzle
from django.urls import path,include
from .utils import write_pgn_chunk_files
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
            pk=pk).values('fen', 'moves').first()
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

    username = cache.get('username')

    if username == None:
        username = set()
    
    username.add(data.username)

    cache.set('username', username, ONE_DAY)

    ip_cache = cache.get('ip_address')
    if ip_cache == None:
        ip_cache = {ip: 1}
    else:
        try:
            ip_cache[ip] += 1
        except:
            ip_cache[ip] = 1

    cache.set('ip_address', ip_cache, ONE_DAY)
    
    if ip_cache[ip] > 5:
        return JsonResponse({'msg' : 'allow only 5 times plz try next day'})
    
    cache.set(ip, ip_cache, ONE_DAY)

    rank = cache.get('rank')
    if rank == None:
        rank = [{'username' : data.username, 'region': data.region, 'score': data.score}]
    else:
        rank.append({'username' : data.username, 'region': data.region, 'score': data.score})
    
    cache.set('rank', rank, 60*60*24)
    
    return JsonResponse(rank,safe=False)

@api.get('/rank')
def get_rank(request):
    try:
      return sorted(cache.get('rank'), key=lambda x: x['score'])
    except:
      return []

@api.get('/username')
def get_username(request, username:str):
    user = cache.get('username')

    if user == None:
        return True
    
    if username in user:
        return False
    else:
        return True



@api.post('/cache')
def clear_all_cache(request, key:ApiKey):
    
    if key.apikey != 'apikey':
        return False

    total_played = cache.get('total')

    if total_played == None:
        total_played = 0

    cache.clear()
    cache.set('total',total_played, ONE_DAY)


    
urlpatterns = [
    path('', api.urls),
    path('sample/', TemplateView.as_view(template_name='puzzle_attack.html'), name='puzzle'),
]
