from __future__ import annotations
from typing import Type
from silhouette_card_maker.models.collections import CardCollection
from silhouette_card_maker.enums import ParserSource, FetcherSource


from silhouette_card_maker import fetchers
from silhouette_card_maker import parsers



PARSERS: dict[str, Type[parsers.BaseParser]] = {
    ParserSource.MPCFILL_XML: parsers.MPCFillXMLParser,
}

FETCHERS: dict[str, Type[fetchers.BaseFetcher]] = {
    FetcherSource.MPCFILL: fetchers.MPCFillFetcher,
}

def get_parser(name: str, **kwargs) -> parsers.BaseParser:
    """
    Return an instantiated parser given its registered name.
    """
    if name not in PARSERS:
        available = ", ".join(_PARSERS.keys()) or "(none registered)"
        raise KeyError(f"Unknown parser '{name}'. Available: {available}")
    return PARSERS[name](**kwargs)

def get_fetcher(name: str, **kwargs) -> fetchers.BaseFetcher:
    """
    Return an instantiated fetcher given its registered name.
    """
    if name not in FETCHERS:
        available = ", ".join(_FETCHERS.keys()) or "(none registered)"
        raise KeyError(f"Unknown fetcher '{name}'. Available: {available}")
    return FETCHERS[name](**kwargs)

def create_collection(parser_name: str, input_file: str) -> CardCollection:
    parser = get_parser(parser_name)
    return parser.parse(input_file)

def create_fetcher(fetcher_name: str, **kwargs) -> fetchers.BaseFetcher:
    return get_fetcher(fetcher_name, **kwargs)
