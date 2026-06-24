import argparse
from agent import summarize
from db import init_db, add_entry, get_list
from pandas import DataFrame


def add_command(text):
    entry = summarize(text)
    add_entry(entry)
    print("Success")


def get_list_command(limit):
    entries = get_list(limit)

    df = DataFrame([entry.model_dump() for entry in entries])

    df = df[["entry_id", "summary", "created_at"]]

    print(df)


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

    match args.command:
        case "add":
            add_command(args.text)
        case "list":
            print(f"Limit: {args.limit}")
            get_list_command(args.limit)


main()
