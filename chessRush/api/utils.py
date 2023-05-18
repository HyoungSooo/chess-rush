import os
from django.conf import settings

def write_pgn_chunk_files(value, name):
    with open(f"{settings.BASE_DIR}/data/{name}", 'wb+') as f:
        f.write(value)
    f.close()