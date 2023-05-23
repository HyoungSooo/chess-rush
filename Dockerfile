# pull official base image
FROM python:3.10-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install mysql dependencies
RUN apt-get update
RUN apt-get install gcc default-libmysqlclient-dev -y

# install dependencies
RUN pip install -U pip setuptools wheel
RUN pip install --upgrade pip
COPY chessRush/requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# copy project
COPY /chessRush .

# Convert plain text files from Windows or Mac format to Unix
RUN apt-get install dos2unix
RUN dos2unix --newfile docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Make entrypoint executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN apt-get install curl -y
RUN apt-get install unzip -y

# Entrypoint dependencies
RUN apt-get install netcat -y

RUN curl -O https://stockfishchess.org/files/stockfish-10-linux.zip
RUN unzip stockfish-10-linux.zip


# run entrypoint.sh
ENTRYPOINT ["bash", "/usr/local/bin/docker-entrypoint.sh"]
