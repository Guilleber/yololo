from enum import Enum

from yololo.clients.the_guardian_client import TheGuardianClient, TheGuardianRSSClient
from yololo.clients.rss_clients import (
    BBCNewsClient,
    NPRClient,
    AlJazeeraClient,
    ProPublicaClient,
    APNewsClient,
    APFactCheckClient,
    ReutersClient,
)


#Have to split into own separate file otherwise it leads to circular import
class Source(Enum):
    THE_GUARDIAN = TheGuardianClient
    THE_GUARDIAN_RSS = TheGuardianRSSClient
    BBC_NEWS = BBCNewsClient
    NPR = NPRClient
    AL_JAZEERA = AlJazeeraClient
    PROPUBLICA = ProPublicaClient
    AP_NEWS = APNewsClient
    AP_FACT_CHECK = APFactCheckClient
    REUTERS = ReutersClient