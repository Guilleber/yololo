from enum import Enum

from yololo.clients.the_guardian_client import TheGuardianClient, TheGuardianRSSClient


#Have to split into own separate file otherwise it leads to circular import
class Source(Enum):
    # THE_GUARDIAN = TheGuardianClient
    THE_GUARDIAN_RSS = TheGuardianRSSClient()