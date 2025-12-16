import random

from elasticsearch import Elasticsearch

from .config import config


def get_es_client() -> Elasticsearch:
    if not config.es.endpoints:
        raise Exception(f"ES endpoints is null or empty")

    es_endpoints = [*config.es.endpoints]
    random.shuffle(es_endpoints)

    return Elasticsearch(
        hosts=es_endpoints,
        basic_auth=(
            config.es.username,
            config.es.password,
        ),
    )
