from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection

from recovery_ia.config import get_settings


@lru_cache
def get_mongo_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(settings.mongodb_uri)


def get_reports_collection() -> Collection:
    """Coleccion de MongoDB donde se guardan los RESULTADOS de salida: cada
    informe clinico generado, junto con la entrada del paciente que lo origino."""
    settings = get_settings()
    return get_mongo_client()[settings.mongodb_db][settings.mongodb_reports_collection]
