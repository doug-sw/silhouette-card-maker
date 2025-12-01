import os

import click
from deck_formats import DeckFormat, parse_deck
from scryfall import get_handle_card as scryfall_get_handle_card
from mpcfill import MPCFillParser
from typing import Set
from pathlib import Path

output_directory = Path(__file__).parents[2] / "game"

@click.command()
@click.argument('deck_path')
@click.argument('format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))
@click.option('-i', '--ignore_set_and_collector_number', default=False, is_flag=True, show_default=True, help="Ignore provided sets and collector numbers when fetching cards.")
@click.option('--prefer_older_sets', default=False, is_flag=True, show_default=True, help="Prefer fetching cards from older sets if sets are not provided.")
@click.option('-s', '--prefer_set', multiple=True, help="Prefer fetching cards from a particular set(s) if sets are not provided. Use this option multiple times to specify multiple preferred sets.")
@click.option('--prefer_showcase', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with showcase treatment")
@click.option('--prefer_extra_art', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with full art, borderless, or extended art.")
@click.option('--tokens', default=False, is_flag=True, show_default=True, help="Fetch related tokens when fetching cards")
@click.option('--parallel', default=False, is_flag=True, show_default=True, help="Download images in parallel")
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
    if not os.path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()
    
    if format == DeckFormat.MPCFILL_XML:
        parser = MPCFillParser()
        cards = parser.parse(deck_text)
        import time
        start = time.perf_counter()
        if parallel:
            parser.fetch_cards_parallel(cards, output_directory)
        else:
            parser.fetch_cards(cards, output_directory)
        end = time.perf_counter()
        print(f'Run time: {end - start}')
    else:
        get_handle_card = scryfall_get_handle_card(
            ignore_set_and_collector_number,

            prefer_older_sets,
            prefer_set,
            
            prefer_showcase,
            prefer_extra_art,
            tokens,

            front_directory,
            double_sided_directory
        )

        parse_deck(
            deck_text,
            format,
            get_handle_card,
        )

if __name__ == '__main__':
    cli()