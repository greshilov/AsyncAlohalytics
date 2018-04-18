import psycopg2
import json


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
            location TEXT,
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


def add_aloha_event_command(aloha_id, platform, bundle, version, events):
    values_list = []
    _, aloha_id = aloha_id.split(':')
    for event in events:
        args = 'to_timestamp({})'.format(event.timestamp), \
               *map(__escape, (aloha_id, platform, bundle, version, event.key,
                               event.value, event.location, json.dumps(event.pairs))),

        values_list.append(__wrap(','.join(args)))

    values = ','.join(values_list)
    return 'INSERT INTO events (timestamp, aloha_id, platform, bundle, version, key, value, location, pairs) ' \
           'VALUES {values}'.format(values=values)


def get_aloha_events_command():
    return 'SELECT aloha_id FROM events'


if __name__ == '__main__':
    create_tables()