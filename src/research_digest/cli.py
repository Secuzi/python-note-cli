import argparse
from agent import summarize
from model import EntryCreate
from db import init_db, add_entry


def add_command(text):
    res = summarize(text)

    entry = EntryCreate.model_validate_json(res)
    add_entry(entry)
    # Check if there is existing tag from entry list

    # If nothing is found then create tag in db (tag_id + name)

    # Get id of tag then create entry_tag row

    # Create row in entry table

    print(f"Output: {entry}")


def init_subparsers(parser):
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add notes for LLM to summarize")

    add_parser.add_argument("--text", required=True, help="The note content")

    list_parser = subparsers.add_parser("list", help="List out all of the entries")
    list_parser.add_argument("--limit", type=int, default=10)


def main():

    init_db()

    parser = argparse.ArgumentParser(description="Cool CLI for studying")

    init_subparsers(parser)
    args = parser.parse_args()

    if args.command == "add":
        print(args.text)
        add_command(args.text)


main()
