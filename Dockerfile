FROM continuumio/miniconda3



RUN mkdir -m777 /app
WORKDIR /app
ADD docker-entrypoint.sh ./
ADD mercure-totalsegmentator ./mercure-totalsegmentator

RUN chmod 777 ./docker-entrypoint.sh


RUN conda create -n env python=3.9
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
RUN chmod -R 777 /opt/conda/envs

RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y git build-essential cmake pigz
RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y libsm6 libxrender-dev libxext6 ffmpeg
RUN apt-get install unzip

ADD environment.yml ./
RUN conda env create -f ./environment.yml

# Pull the environment name out of the environment.yml
RUN echo "source activate $(head -1 ./environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 ./environment.yml | cut -d' ' -f2)/bin:$PATH

RUN python -m pip uninstall -y opencv-python
RUN python -m pip install opencv-python==4.5.5.64

ENV TOTALSEG_HOME_DIR=/app/.totalsegmentator
RUN /opt/conda/envs/mercure-totalsegmentator/bin/totalseg_download_weights -t total
RUN /opt/conda/envs/mercure-totalsegmentator/bin/totalseg_download_weights -t total_fast
RUN /opt/conda/envs/mercure-totalsegmentator/bin/totalseg_download_weights -t total_mr
RUN /opt/conda/envs/mercure-totalsegmentator/bin/totalseg_download_weights -t total_fast_mr

WORKDIR /app

CMD ["./docker-entrypoint.sh"]
