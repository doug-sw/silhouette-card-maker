from enum import StrEnum

class FaceType(StrEnum):
	FRONT = "front"
	BACK = "back"

class Game(StrEnum):
    MTG = "mtg"
    POKEMON = "pokemon"

class ParserSource(StrEnum):
    SIMPLE = "simple"
    MTGA = "mtga"
    MTGO = "mtgo"
    ARCHIDEKT = "archidekt"
    DECKSTATS = "deckstats"
    MOXFIELD = "moxfield"
    SCRYFALL_JSON = "scryfall_json"
    MPCFILL_XML = "mpcfill_xml"

class FetcherSource(StrEnum):
    MPCFILL = "mpcfill"
    SCRYFALL = "scryfall"
