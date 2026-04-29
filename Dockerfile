FROM ghcr.io/astral-sh/uv:python3.10-bookworm AS base

RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -qy --no-install-recommends \
        crudini \
        git \
        postgresql-client

WORKDIR /usr/lib/ckan

COPY ckanext/ ckanext/
COPY dummy/ dummy/
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,sharing=locked,target=/root/.cache/uv \
    uv sync --locked --no-dev

COPY entrypoint/custom-entrypoint.sh entrypoint/dev-entrypoint.sh /
RUN chmod +x /custom-entrypoint.sh /dev-entrypoint.sh

ENV CKAN_HOME=/usr/lib/ckan
ENV CKAN_VENV=$CKAN_HOME/.venv
ENV CKAN_CONFIG=$CKAN_VENV/lib/python3.10/site-packages/ckan/config
ENV CKAN_INI=/srv/app/ckan.ini
ENV CKAN_STORAGE_PATH=/var/lib/ckan

RUN mkdir -p $CKAN_STORAGE_PATH/webassets/.webassets-cache

ENV PATH="$CKAN_VENV/bin:$PATH"

ENTRYPOINT ["/bin/bash", "/custom-entrypoint.sh"]
CMD ["ckan", "run", "--host", "0.0.0.0"]
