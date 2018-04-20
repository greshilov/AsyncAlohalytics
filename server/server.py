#!/usr/bin/python

import aiopg
import tornado.platform.asyncio
import asyncio
import json

try:
    import pyalohareciever
except ImportError:
    print('Please build \'pyalohareciever.so\' first: \'bin/build.sh\'')

from tornado.web import RequestHandler, Application, StaticFileHandler
from tornado.httpserver import HTTPServer
from db import add_aloha_event_command, get_aloha_events_command
from utils import CONFIG, app_log, json_serial, STATIC_PATH


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    async def execute(self, cmd, args):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(cmd, args)

    async def fetch(self, cmd, args):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(cmd, args)
                ret = []
                async for row in cur:
                    ret.append(row)
        return ret


class AlohaMessagesHandler(BaseHandler):
    async def post(self, platform, bundle_id, version):
        try:
            # Execution time ~ 0.1 ms -> non-blocking
            aloha_id, events = pyalohareciever.decode(self.request.body)

            async with self.db.acquire() as conn:
                async with conn.cursor() as cur:
                    await add_aloha_event_command(cur, aloha_id, platform, bundle_id, version, events)

        except RuntimeError:
            app_log.error('Corrupted message body, bundle_id: '
                          '{}, version: {}, platform: {}'.format(platform, bundle_id, version))


class MaxEventHandler(BaseHandler):
    async def get(self):
        events = await self.fetch('SELECT last_value FROM events_event_id_seq', tuple())
        self.set_header('Access-Control-Allow-Origin', '*')
        if events:
            self.write(str(events[0][0]))
        else:
            self.write('0')


class FrontEndHandler(BaseHandler):
    @property
    def db(self):
        return self.application.db

    async def get(self):
        aloha_id = self.get_argument('aloha_id', '', True)
        key = self.get_argument('key', '', True)
        value = self.get_argument('value', '', True)
        timestamp = self.get_argument('timestamp', '', True)
        limit = self.get_argument('limit', '', True)
        offset = self.get_argument('offset', '', True)
        cmd, c_cmd, args = get_aloha_events_command(aloha_id=aloha_id, key=key, value=value,
                                                    timestamp=timestamp, limit=limit, offset=offset)

        events = await self.fetch(cmd, args)
        # count for pagination
        count = await self.fetch(c_cmd, args)
        count = count[0][0] if count else 0
        response = {'events': events, 'count': count}
        self.write(json.dumps(response, default=json_serial))
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.finish()


async def create_pool():
    return await aiopg.create_pool(dsn='dbname={dbname} user={user} password={password} '
                                       'host={host} port={port}'.format(**CONFIG['db']))


if __name__ == '__main__':
    application = Application((
        (r'/(android|ios)/(\S+)/(\S+)', AlohaMessagesHandler),
        (r'/events/max/', MaxEventHandler),
        (r'/events/', FrontEndHandler),
        (r'/(.*)', StaticFileHandler, {'path': STATIC_PATH, 'default_filename': 'index.html'}),
    ))

    tornado.platform.asyncio.AsyncIOMainLoop().install()
    ioloop = asyncio.get_event_loop()

    application.db = ioloop.run_until_complete(create_pool())

    http_server = HTTPServer(application, decompress_request=True)
    http_server.listen(CONFIG['server']['port'], CONFIG['server']['host'])

    ioloop.run_forever()
