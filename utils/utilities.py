import re
import datetime
from zoneinfo import ZoneInfo
import os
from faker import Faker
from faker.providers import lorem


def generate_id(Paste, length=6) -> str:
    word_generator = Faker()
    word_generator.add_provider(lorem)
    while True:
        new_id = "-".join(word_generator.words(nb=3, part_of_speech="noun"))
        if not Paste.query.filter_by(id=new_id).first():
            return new_id


def is_url(value: str) -> bool:
    """
    Returns True if *value* looks like a URL.
    """
    # The same pattern we used in the template, but compiled once here.
    pattern = re.compile(
        r"^(https?://)?"  # optional scheme
        r"([\w.-]+)\."  # sub‑domain / domain
        r"[a-z]{2,}"  # TLD (at least two letters)
        r"(/[\\w./?%&=-]*)?$"  # optional path / query
    )
    return bool(pattern.match(value))


def set_to_timezone(
        naive_ts,
        tz=os.getenv("PASTEBIN_TIMEZONE", "America/Los_Angeles")
        ):
    utc_dt = naive_ts.replace(tzinfo=datetime.timezone.utc)
    return utc_dt.astimezone(ZoneInfo(tz))
