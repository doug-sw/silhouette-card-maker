import os
import time
from pathlib import Path
from typing import Set

import click

from silhouette_card_maker.models import Card
from silhouette_card_maker.parsers.mpcfill import MPCFillParser
from silhouette_card_maker.fetchers.mpcfill import MPCFillCardImageFetcher
from silhouette_card_maker.formats import DeckFormat


BASE_OUTPUT_DIR = Path(__file__).parents[1] / "game"

@click.command()
@click.argument('deck_path')
@click.argument('format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))
@click.option('-i', '--ignore_set_and_collector_number', default=False, is_flag=True, show_default=True, help="Ignore provided sets and collector numbers when fetching cards.")
@click.option('--prefer_older_sets', default=False, is_flag=True, show_default=True, help="Prefer fetching cards from older sets if sets are not provided.")
@click.option('-s', '--prefer_set', multiple=True, help="Prefer fetching cards from a particular set(s) if sets are not provided. Use this option multiple times to specify multiple preferred sets.")
@click.option('--prefer_showcase', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with showcase treatment")
@click.option('--prefer_extra_art', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with full art, borderless, or extended art.")
@click.option('--tokens', default=False, is_flag=True, show_default=True, help="Fetch related tokens when fetching cards")
@click.option('--parallel', default=False, is_flag=True, show_default=True, help="Download images in parallel (limited to mpcfill_xml).")
def cli(
    deck_path: str,
    format: DeckFormat,
    ignore_set_and_collector_number: bool,
    prefer_older_sets: bool,
    prefer_set: Set[str],
    prefer_showcase: bool,
    prefer_extra_art: bool,
    tokens: bool,
    parallel: bool,
):
    deck_path = Path(deck_path)
    if not deck_path.is_file():
        print(f"{deck_path} is not a valid file.")
        return

    with deck_path.open("r", encoding="utf-8") as f:
        deck_text = f.read()

    output_dir = BASE_OUTPUT_DIR
    front_dir = output_dir / "front"
    double_sided_dir = output_dir / "double_sided"

    if format == DeckFormat.MPCFILL_XML:
        parser = MPCFillParser()
        cards = parser.parse(deck_text)

        fetcher = MPCFillCardImageFetcher()
        start = time.perf_counter()
        if parallel:
            fetcher.fetch_cards_parallel(cards, output_dir)
        else:
            fetcher.fetch_cards(cards, output_dir)
        end = time.perf_counter()
        print(f"Run time: {end - start:.2f}s")

    else:
        raise NotImplementedError("I have a limited number of braincells available.")
        # get_handle = scryfall_get_handle_card(
        #     ignore_set_and_collector_number,
        #     prefer_older_sets,
        #     prefer_set,
        #     prefer_showcase,
        #     prefer_extra_art,
        #     tokens,
        #     front_dir,
        #     double_sided_dir,
        # )
        # parse_deck(deck_text, format, get_handle)


if __name__ == "__main__":
    cli()