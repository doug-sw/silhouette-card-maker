import argparse
from pathlib import Path
from silhouette_card_maker.factory import get_parser, get_fetcher
from silhouette_card_maker.enums import ParserSource, FetcherSource


BASE_OUTPUT_DIR = Path(__file__).parents[1] / "game"


def main():
    parser = argparse.ArgumentParser(description="Download card images from various sources.")
    parser.add_argument("--input-file", required=True, help="Path to the input file (XML, JSON, etc.)")
    parser.add_argument("--parser-source", required=True, type=str,
                        help=f"Parser source key ({', '.join([p.value for p in ParserSource])})")
    parser.add_argument("--fetcher-source", required=True, type=str,
                        help=f"Fetcher source key ({', '.join([f.value for f in FetcherSource])})")
    parser.add_argument("--output-dir", type=str, default=str(BASE_OUTPUT_DIR),
                        help=f"Directory to store downloaded images (default: {BASE_OUTPUT_DIR})")
    parser.add_argument("--parallel", action="store_true", help="Use parallel download if supported")
    parser.add_argument("--max-workers", type=int, default=None, help="Max workers for parallel download")

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    parser_source = ParserSource(args.parser_source)
    fetcher_source = FetcherSource(args.fetcher_source)

    parser_instance = get_parser(parser_source)
    fetcher_instance = get_fetcher(fetcher_source)

    raw_data = input_path.read_text()
    collection = parser_instance.parse(raw_data)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.parallel:
        fetcher_instance.fetch_parallel(collection, output_dir, max_workers=args.max_workers)
    else:
        fetcher_instance.fetch(collection, output_dir)

    print(f"Downloaded {len(collection.cards)} cards to {output_dir}")

if __name__ == "__main__":
    main()
