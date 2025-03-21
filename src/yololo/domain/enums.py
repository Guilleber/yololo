from enum import Enum


class Language(str, Enum):
    ENGLISH = 'en'
    FRENCH = 'fr'


class Source(str, Enum):
    THE_GUARDIAN = 'the_guardian'
