import enum

class DeckFormat(str, enum.Enum):
    SIMPLE = "simple"
    MTGA = "mtga"
    MTGO = "mtgo"
    ARCHIDEKT = "archidekt"
    DECKSTATS = "deckstats"
    MOXFIELD = "moxfield"
    SCRYFALL_JSON = "scryfall_json"
    MPCFILL_XML = "mpcfill_xml"

