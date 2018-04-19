import psycopg2
import json
import re

LAT_RE = re.compile(r'lat=([+-]?([0-9]*[.])?[0-9]+)')
LON_RE = re.compile(r'lon=([+-]?([0-9]*[.])?[0-9]+)')


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        DROP TYPE IF EXISTS PLATFORM_TYPE;
        CREATE TYPE PLATFORM_TYPE AS ENUM ('android', 'ios');
        
        CREATE TABLE events (
            event_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            aloha_id VARCHAR(36) NOT NULL,
            platform PLATFORM_TYPE NOT NULL,
            bundle VARCHAR(255) NOT NULL,
            version VARCHAR(5) NOT NULL,
            key VARCHAR(255) NOT NULL,
            value VARCHAR(255),
            location JSON,
            pairs JSON
        )
        """,)
    conn = None
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect(host='localhost', user='python', password='python', dbname='postgres')
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def __wrap(event_str):
    return '({})'.format(event_str)


def __escape(element):
    return '\'{}\''.format(str(element))


def __parse_location(location):
    lat_match = LAT_RE.search(location)
    lon_match = LON_RE.search(location)
    if lat_match and lon_match:
        lat, lon = lat_match.group(1), lon_match.group(1)
        if lat != 0 or lon != 0:
            return __escape(json.dumps({'lat': lat, 'lon': lon}))
    return '\'{}\''


def add_aloha_event_command(aloha_id, platform, bundle, version, events):
    values_list = []
    _, aloha_id = aloha_id.split(':')
    for event in events:
        args = 'to_timestamp({})'.format(event.timestamp), \
               __parse_location(event.location), \
               *map(__escape, (aloha_id, platform, bundle, version, event.key,
                               event.value, json.dumps(event.pairs))),

        values_list.append(__wrap(','.join(args)))

    values = ','.join(values_list)
    return 'INSERT INTO events (timestamp, location, aloha_id, platform, bundle, version, key, value, pairs) ' \
           'VALUES {values}'.format(values=values)


def get_aloha_events_command(aloha_id=None, key=None, value=None, timestamp=None, limit=30):
    where_keys = []
    where = ''
    if aloha_id:
        where_keys.append('aloha_id LIKE \'%{aloha_id}%\''.format(aloha_id=aloha_id))
    if key:
        where_keys.append('key LIKE \'%{key}%\''.format(key=key))
    if value:
        where_keys.append('value LIKE \'%{value}%\''.format(value=value))
    if timestamp:
        where_keys.append('timestamp > NOW() - INTERVAL \'%{timestamp}%\''.format(timestamp=timestamp))

    if where_keys:
        where = 'WHERE ' + ' AND '.join(where_keys)

    try:
        limit = int(limit)
        if limit > 50:
            limit = 50
    except ValueError:
        limit = 30

    return """SELECT event_id, aloha_id, platform, key, value, location, pairs, timestamp 
              FROM events {where} ORDER BY event_id DESC LIMIT {limit}""".format(where=where, limit=limit)


if __name__ == '__main__':
    create_tables()