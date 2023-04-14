import asyncio
from typing import Optional, Awaitable

import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


async def main():
    app = make_app()
    app.listen(6333)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
