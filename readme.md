# Chess-Rush

demo page => https://www.chess-rush.kro.kr/api/sample/

### Version 0.0.1
* Can play Chess rush mode.
* Ranking can be registered 5 times a day
* You can customize your own chess problems
```shell
endpoint => POST /api/upload

schema => {
  apikey :str
}

endpoint => POST /api/upload/file/puzzle
``` 
Since it is still in the development stage, the key authentication part is weak.
Also, the name of the uploaded file must be 'lichess_db_puzzle.csv'
Plan to add custom file names and non-vulnerable apikey authentication logic during version upgrade later.
Therefore, I still want to run it only in the local environment.



All ranking data is initialized at 00:00 Korean standard time every day.



There is no verification logic to register for ranking.
The only authentication feature is the user's IP address, which limits the ranking to 5 times a day.


run command
```shell
clone https://github.com/HyoungSooo/chess-rush.git
docker-compose up
```

### In Version 0.0.2 update content
* To be made into a library(using pip)
* autochess mode
* community
