FROM continuumio/anaconda3:latest

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libncurses5-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN conda env create -f ibd_env.yml

EXPOSE 8501

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "ancibd_py310", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]
