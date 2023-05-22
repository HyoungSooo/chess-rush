import os
from django.conf import settings
from stockfish import Stockfish

def write_pgn_chunk_files(value, name):
    with open(f"{settings.BASE_DIR}/data/{name}", 'wb+') as f:
        f.write(value)
    f.close()


def get_stockfish():
    os.chdir(f"{settings.BASE_DIR}/api/stockfish_10_linux/Linux")
    file_dir = os.getcwd()

    stockfish = Stockfish(
        path=file_dir + '/stockfish_10_x64')

    return stockfish

import random

def create_random_fen(total):
    count = 0
    ans = []
    while True:
        q = random.randint(0, 5)
        r = random.randint(0, 9)
        n = random.randint(0, 15)
        b = random.randint(0, 15)
        p = 45 - (q*9 + r*5 + n*3 + b*3)
        if p >= 0:
            if q+r+n+b+p > 15:
              continue
            count += 1
            fen = ['q']*q + ['r']*r + ['n']*n + ['b']*b + ['p']*p + ['k'] + [0] * (32 - (q+r+n+b+p + 1))

            while True:

              random.shuffle(fen)

              new_lst = [fen[i:i+8] for i in range(0,len(fen),8)]

              if 'k' in new_lst[0] or 'k' in new_lst[1]:
                  break
                  
            result = ''
            for row in new_lst:
                cnt = 0
                for item in row:
                    if item == 0:
                        cnt +=1
                    else:
                        if cnt > 0:
                            result += str(cnt)
                            cnt = 0
                        result += str(item)
                if cnt > 0:
                    result += str(cnt)
                result += '/'
            result = result[:-1] + '/'
            ans.append(result)
        if count == total:
            break
        

    return ans
