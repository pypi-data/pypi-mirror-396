ARG UV_VERSION=0.6

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv_image
FROM gitlab-registry.mpcdf.mpg.de/nomad-lab/nomad-fair:develop

USER root

RUN apt-get update \
 && apt-get install --yes --quiet --no-install-recommends \
      libgomp1 \
      libmagic1 \
      file \
      gcc \
      build-essential \
      curl \
      zip \
      unzip \
      git \
 && rm -rf /var/lib/apt/lists/*
 
# install uv
COPY --from=uv_image /uv /bin/uv
 

COPY nomad.yaml .

RUN mkdir data
COPY data/upload-navigation.zip data/

COPY . .

ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NOMAD_GUI=0.0 


RUN uv pip install ".[dev]" -p /opt/venv

RUN chown -R nomad:1000 /app

RUN python \
     compress_upload.py \
     "src/nomad_gui/example_uploads/layout_demonstration" \
     --upload-name layout_demonstration.zip \
     --ignore-path-prefix

# revert back to nomad user
USER nomad


