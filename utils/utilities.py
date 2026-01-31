import string
import random
import re
import datetime
from zoneinfo import ZoneInfo 
import os

def generate_id(Paste, length=6) -> str:
    characters = string.ascii_letters + string.digits
    while True:
        new_id = ''.join(random.choice(characters) for _ in range(length))
        if not Paste.query.filter_by(id=new_id).first():
            return new_id

def is_url(value: str) -> bool:
    """
    Returns True if *value* looks like a URL.
    """
    # The same pattern we used in the template, but compiled once here.
    pattern = re.compile(
        r'^(https?://)?'          # optional scheme
        r'([\w.-]+)\.'            # sub‑domain / domain
        r'[a-z]{2,}'              # TLD (at least two letters)
        r'(/[\\w./?%&=-]*)?$'     # optional path / query
    )
    return bool(pattern.match(value))

def set_to_timezone(naive_ts, tz=os.getenv('PASTEBIN_TIMEZONE', "America/Los_Angeles")):
    utc_dt = naive_ts.replace(tzinfo=datetime.timezone.utc)
    return utc_dt.astimezone(ZoneInfo(tz))