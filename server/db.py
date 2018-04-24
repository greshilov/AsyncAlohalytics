import psycopg2
import psycopg2.extensions
import json
import re
import argparse

from utils import CONFIG, app_log, MAX_LIMIT, DEFAULT_LIMIT

LAT_RE = re.compile(r'lat=([+-]?([0-9]*[.])?[0-9]+)')
LON_RE = re.compile(r'lon=([+-]?([0-9]*[.])?[0-9]+)')


class db_connection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        # connect to the PostgreSQL server
        self.connection = psycopg2.connect(**CONFIG['db'])
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        if exc_type is None:
            self.connection.commit()
        self.connection.close()


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        DROP TYPE IF EXISTS PLATFORM_TYPE;
        CREATE TYPE PLATFORM_TYPE AS ENUM ('android', 'ios');

        CREATE TABLE events (
            event_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            aloha_id VARCHAR(38) NOT NULL,
            platform PLATFORM_TYPE NOT NULL,
            bundle VARCHAR(255) NOT NULL,
            version VARCHAR(8) NOT NULL,
            key VARCHAR(255) NOT NULL,
            value VARCHAR(255),
            location JSON,
            pairs JSON
        )
        """,)

    with db_connection() as cursor:
        for command in commands:
            cursor.execute(command)


def drop_tables():
    with db_connection() as cursor:
        cursor.execute('DROP TABLE IF EXISTS events')


def delete_old_events():
    app_log.debug('Deleting old events...')
    with db_connection() as cursor:
        cursor.execute('DELETE FROM events WHERE timestamp > NOW() - INTERVAL %s', ('2 weeks', ))


def __to_regexp(element):
    return '%{}%'.format(str(element))


def __parse_location(location):
    lat_match = LAT_RE.search(location)
    lon_match = LON_RE.search(location)
    if lat_match and lon_match:
        lat, lon = lat_match.group(1), lon_match.group(1)
        if lat != 0 or lon != 0:
            return json.dumps({'lat': lat, 'lon': lon})
    return '{}'


async def add_aloha_event_command(cursor, aloha_id, platform, bundle, version, events):
    values_list = []
    for event in events:
        value = await cursor.mogrify('(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s)',
                                     (event.timestamp, __parse_location(event.location), aloha_id, platform, bundle,
                                      version, event.key, event.value, json.dumps(event.pairs)))
        values_list.append(value.decode('utf8'))

    values = ','.join(values_list)
    query = 'INSERT INTO events (timestamp, location, aloha_id, platform, bundle, version, key, value, pairs) ' \
            'VALUES {values}'.format(values=values)
    await cursor.execute(query)


def get_aloha_events_command(aloha_id=None, key=None, value=None, timestamp=None, limit=30, offset=0):
    where_keys = []
    where_strings = []
    where = ''

    if aloha_id:
        where_strings.append('aloha_id LIKE %s')
        where_keys.append(__to_regexp(aloha_id))
    if key:
        where_strings.append('key ILIKE %s')
        where_keys.append(__to_regexp(key))
    if value:
        where_strings.append('value ILIKE %s')
        where_keys.append(__to_regexp(value))

    if timestamp:
        where_strings.append('timestamp > NOW() - INTERVAL %s')
        where_keys.append(timestamp)

    if where_keys:
        where = 'WHERE ' + ' AND '.join(where_strings)

    try:
        limit = int(limit)
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT
    except ValueError:
        limit = DEFAULT_LIMIT

    try:
        offset = int(offset)
    except ValueError:
        offset = 0

    command = """
        SELECT event_id, aloha_id, platform, key, value, location, pairs, timestamp
        FROM events {where} ORDER BY event_id DESC LIMIT {limit} OFFSET {offset}
        """.format(where=where, limit=limit, offset=offset)

    count_command = """
        SELECT COUNT(event_id) FROM events {where}
        """.format(where=where)

    return command, count_command, tuple(where_keys)


if __name__ == '__main__':
    drop_tables()
    create_tables()
