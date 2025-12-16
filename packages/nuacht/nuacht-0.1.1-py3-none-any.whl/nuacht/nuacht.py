import logging
import sqlite3
import time
from dataclasses import astuple, dataclass
from pathlib import Path
from sqlite3 import Cursor
from typing import Generator

import feedparser
from feedparser import FeedParserDict

config_dir = Path('~/.nuacht').expanduser()
config_dir.mkdir(parents=True, exist_ok=True)
log_file = Path(config_dir, 'out.log')
db_file = Path(config_dir, 'entries.db')
feeds = Path(config_dir, 'feeds.rss')


@dataclass
class Entry:
    url: str
    title: str
    summary: str
    thumbnail: str
    published: int
    tags: str

    def __str__(self) -> str:
        return f'{self.url=} {self.title=} {self.summary=} {self.thumbnail=} {self.published=}'

    def __bool__(self) -> bool:
        return all([self.title, self.url, self.published])

    def err(self) -> str:
        errors = ''
        invalid = [k for k, v in vars(self).items() if not v]
        conj = 'are' if len(invalid) > 1 else 'is'

        while invalid:
            invalid_attr = invalid.pop(0)
            errors += invalid_attr

            if invalid:
                errors += ', '

        return f'{errors} {conj} invalid' if errors else 'No errors'


def set_up_logging(level: int) -> None:
    logging.basicConfig(
        filename=log_file,
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def feeds_iter() -> Generator[tuple[str, FeedParserDict], None, None]:
    if not feeds.exists():
        logging.error(f'{str(feeds)} not found.')
        return

    with open(feeds, 'r', encoding='utf-8') as f:
        feeds_list = [url for url in f.read().split('\n') if url]

    if not feeds_list:
        logging.error('No feeds listed')
        return

    logging.info('Iterating feeds.')

    while feeds_list:
        url = feeds_list.pop(0).strip()
        logging.info(f'Parsing "{url}".')

        yield url, feedparser.parse(url)


def is_feed_valid(url: str, feed: FeedParserDict) -> bool:
    logging.info(f'Validating "{url}".')

    if all(['bozo' in feed, feed.bozo]):
        logging.error(f'Bozo in {url}: [{type(feed.bozo_exception).__name__}] {feed.bozo_exception}.')
        return False
    elif any(['entries' not in feed, not len(feed.entries)]):
        logging.error(f'No entries in {url}.')
        return False
    else:
        return True


def parse_url(entry: FeedParserDict) -> str:
    return entry.link if 'link' in entry else ''


def parse_title(entry: FeedParserDict) -> str:
    return entry.title if 'title' in entry else ''


def parse_summary(entry: FeedParserDict) -> str:
    return entry.summary if 'summary' in entry else ''


def get_max_thumbnail_size(content: list[dict]) -> str:
    return max(content, key=lambda c: int(c['width']))['url']


def parse_thumbnail(entry: FeedParserDict) -> str:
    if 'media_thumbnail' in entry:
        return get_max_thumbnail_size(entry.media_thumbnail)
    elif 'media_content' in entry:
        return get_max_thumbnail_size(entry.media_content)
    else:
        return ''


def parse_published(entry: FeedParserDict) -> int:
    return int(time.mktime(entry.published_parsed)) if 'published_parsed' in entry else -1


def parse_tags(entry: FeedParserDict) -> str:
    return ','.join(list(map(lambda t: t.term, entry.tags))) if 'tags' in entry else ''


def parse_entry(entry: FeedParserDict) -> Entry:
    return Entry(
        url=parse_url(entry),
        title=parse_title(entry),
        summary=parse_summary(entry),
        thumbnail=parse_thumbnail(entry),
        published=parse_published(entry),
        tags=parse_tags(entry)
    )


def entries_iter(feed: FeedParserDict) -> Generator[Entry, None, None]:
    logging.info('Iterating entries.')

    for entry in feed.entries:
        yield parse_entry(entry)


def store_entry_in_database(entry: Entry, cur: Cursor) -> None:
    logging.info(f'Inserting {entry.title} into database.')

    cur.execute(
        """
            INSERT OR IGNORE INTO entries (url, title, summary, thumbnail, time, tags) VALUES (?, ?, ?, ?, ?, ?)
        """,
        astuple(entry)
    )


def delete_older_entries(cur: Cursor, duration: int, verbose: bool) -> None:
    if duration < 0:
        logging.info('Not deleting entries.')
        return

    logging.info(f'Deleting entries older than {duration=}.')

    if verbose:
        cur.execute(f"""SELECT * FROM entries WHERE time < strftime('%s', 'now') - {duration}""")
        rows = cur.fetchall()

        logging.info('Removing entries: ' if rows else 'No entries to remove.')

        for row in rows:
            logging.info(row)

    cur.execute(f"""
        DELETE FROM entries WHERE time < strftime('%s', 'now') - {duration}
    """)


def try_create_table(cur: Cursor) -> None:
    logging.info('Creating table if one does not exist.')

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            summary TEXT,
            thumbnail TEXT,
            time INTEGER NOT NULL,
            tags TEXT
        )
    """)


def insert_into_database(duration: int = -1, verbose: bool = False) -> None:
    """Duration as a UNIX timestamp"""
    set_up_logging(logging.INFO if verbose else logging.WARN)

    logging.info('Running nuacht.')
    logging.info(f'Opening connection to {db_file}.')

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    try_create_table(cur)

    try:
        for url, feed in feeds_iter():
            if not is_feed_valid(url, feed):
                continue

            for entry in entries_iter(feed):
                if not entry:
                    logging.error(f'{url}: {entry.err()}')
                    continue

                store_entry_in_database(entry, cur)
    except Exception as e:
        logging.exception(e)
    else:
        delete_older_entries(cur, duration, verbose)

        logging.info('Committing changes.')
        conn.commit()
    finally:
        logging.info('Closing connection and exiting.')
        conn.close()
