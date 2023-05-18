from api.models import ChessPuzzle
from django.core.management.color import no_style
import pandas as pd
from api.models import ChessPuzzle
import chess
from multiprocessing import Pool
from django.conf import settings


class PuzzleProcess:
    def puzzle_run(self):
        chunk_size = 10**3
        col = "PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningFamily,OpeningVariation"
        fpath = f"{settings.BASE_DIR}/data/lichess_db_puzzle.csv"
        point = ChessPuzzle.objects.count() // 1000

        for cnt, chunk in enumerate(pd.read_csv(fpath, chunksize=chunk_size, delimiter=',', header=None, names=col.split(','))):
            print(chunk.head())
            if cnt < point:
                continue
            
            puzzle = []

            for idx, row in chunk.iterrows():

                puzzle.append(ChessPuzzle(fen=row['FEN'], moves=row['Moves'], url=row['GameUrl'],
                                                         opening_fam=row['OpeningFamily'], opening_variation=row['OpeningVariation'], theme=row['Themes']))
                
                ChessPuzzle.objects.bulk_create(puzzle)
