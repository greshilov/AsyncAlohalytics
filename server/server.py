#!/usr/bin/python

import momoko
import pyalohareciever
import logging

from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from db import add_aloha_event_command, get_aloha_events_command
from utils import CONFIG, app_log


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db


class AlohaMessagesHandler(BaseHandler):
    async def post(self, platform, bundle_id, version):
        try:
            # Execution time ~ 0.1 ms -> non-blocking
            aloha_id, events = pyalohareciever.decode(self.request.body)
            cmd = add_aloha_event_command(aloha_id, platform, bundle_id, version, events)
            await self.db.execute(cmd)
        except RuntimeError:
            app_log.error('Corrupted message body, bundle_id: '
                          '{}, version: {}, platform: {}'.format(platform, bundle_id, version))


class FrontEndHandler(BaseHandler):
    @property
    def db(self):
        return self.application.db

    async def get(self):
        cursor = await self.db.execute(get_aloha_events_command())
        self.write("Results: %s" % cursor.fetchall())
        self.finish()


if __name__ == '__main__':
    application = Application((
        (r'/(android|ios)/(\S+)/(\d+)', AlohaMessagesHandler),
        (r'/', FrontEndHandler)
    ))

    ioloop = IOLoop.instance()

    application.db = momoko.Pool(
        dsn='dbname={name} user={user} password={password} '
            'host={host} port={port}'.format(**CONFIG['db']),
        size=CONFIG['db']['workers'],
        ioloop=ioloop,
    )

    # this is a one way to run ioloop in sync
    future = application.db.connect()
    ioloop.add_future(future, lambda f: ioloop.stop())
    ioloop.start()
    future.result()

    http_server = HTTPServer(application, decompress_request=True)
    http_server.listen(CONFIG['server']['port'], CONFIG['server']['host'])

    ioloop.start()



