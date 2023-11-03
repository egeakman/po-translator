from argparse import ArgumentParser
from pathlib import Path

from po_translator.translator import POFileTranslator


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "file",
        metavar="library/stdtypes.po",
        help="po file path to be translated",
        type=Path,
    )
    parser.add_argument(
        "--api",
        metavar="deepl",
        help="translation API to use",
        default="deepl",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--source-lang",
        metavar="auto",
        help="source language",
        default="auto",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--target-lang",
        metavar="en",
        help="target language",
        default="en",
        type=str,
    )
    advanced = parser.add_argument_group("advanced options")
    advanced.add_argument(
        "-p",
        "--proxies",
        help="proxies to use",
        default=None,
        type=str,
    )
    advanced.add_argument(
        "-e",
        "--exclude-patterns",
        help="exclude patterns",
        default=None,
        type=str,
    )
    advanced.add_argument(
        "--skip-translated", help="skip already translated entries", action="store_true"
    )
    advanced.add_argument(
        "--retranslate-fuzzy", help="retranslate fuzzy entries", action="store_true"
    )
    args = parser.parse_args()

    if any([args.proxies, args.exclude_patterns]):
        raise NotImplementedError(
            "Use the library instead of the CLI for excluding patterns and proxies"
        )

    translator = POFileTranslator(
        path=args.file,
        api=args.api,
        source_lang=args.source_lang,
        target_lang=args.target_lang,
    )
    translator.translate(args.skip_translated, args.retranslate_fuzzy)
    translator.save()


if __name__ == "__main__":
    main()
