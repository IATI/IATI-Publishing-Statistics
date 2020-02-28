import argparse
import statsrunner.loop
import statsrunner.aggregate
import statsrunner.invert
import datetime
import re


def parse_date(x):
    xsDateRegex = re.compile('(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})')
    m = xsDateRegex.match(x)
    if m:
        return datetime.date(*map(int, m.groups()))
    else:
        raise ValueError


def calculate_stats():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        help="Output extra debugging information",
        action="store_true"
    )
    parser.add_argument(
        "--strict",
        help="Follow the schema strictly. (This is not currently used by the dashboard stats).",
        action="store_true"
    )
    parser.add_argument(
        "--output",
        help="Output directory. Defaults to out",
        default='out'
    )
    parser.add_argument(
        "--multi",
        help="Number of processes to use. Defaults to 1",
        default=1,
        type=int
    )
    parser.add_argument(
        "--stats-module",
        help="Python module to import stats from, defaults to stats.dashboard",
        default='stats.dashboard'
    )
    parser.add_argument(
        "--verbose-loop",
        help="",
        action="store_true"
    )
    parser.add_argument(
        "--today",
        help="",
        type=parse_date,
        default=datetime.date.today()
    )
    subparsers = parser.add_subparsers()

    parser_loop = subparsers.add_parser(
        'loop',
        help='Loop over every activity organisation, and output JSON'
    )
    parser_loop.add_argument(
        "--folder",
        help="Limit to a specific folder in the data"
    )
    parser_loop.add_argument(
        "--data",
        help="Data directory",
        default='data'
    )
    parser_loop.add_argument(
        "--new",
        help="Only create new files, don't overwrite existing ones",
        action="store_true"
    )
    parser_loop.set_defaults(func=statsrunner.loop.loop)

    parser_aggregate = subparsers.add_parser(
        'aggregate',
        help='Aggregate the per activity JSON into per file and per publisher JSON.'
    )
    parser_aggregate.set_defaults(func=statsrunner.aggregate.aggregate)

    parser_invert = subparsers.add_parser(
        'invert',
        help="'invert' the aggregated JSON. ie. produce JSON that lists publishers and files with each value"
    )
    parser_invert.set_defaults(func=statsrunner.invert.invert)

    args = parser.parse_args()
    args.func(args)
