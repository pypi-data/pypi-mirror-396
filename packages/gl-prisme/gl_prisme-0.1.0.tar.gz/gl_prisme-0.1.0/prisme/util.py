from datetime import date
from time import strptime


def parse_isodate(input: str) -> date:
    return date(*(strptime(input, "%Y-%m-%d")[0:3]))
