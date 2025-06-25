FROM python:3.12

RUN apt-get update && apt-get install -y \
  build-essential \
  python3-dev \
  libffi-dev \
  libxml2-dev \
  libxslt1-dev \
  libjpeg-dev \
  zlib1g-dev \
  libpng-dev \
  libglib2.0-dev \
  libdbus-1-dev \
  libdbus-glib-1-dev \
  libgirepository1.0-dev \
  libcairo2-dev \
  gir1.2-gtk-3.0 \
  libcurl4-openssl-dev \
  pkg-config \
  curl \
  jq \
  git &&\
  rm -rf /var/lib/apt/lists/*

WORKDIR /lib

RUN git clone https://github.com/coreyMerritt/bash-test.git

WORKDIR /opt/blackjack-engine

COPY . .

RUN pip install --upgrade pip &&\
  pip install -r requirements.txt &&\
  ln -s zz-test-client/test.sh test

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
