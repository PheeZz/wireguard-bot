import asyncio
import aiohttp
from aiohttp import web
import socket
import ssl
# webhook that will catch payment notifications from yookassa


async def handle_webhook(request):
    data = await request.json()
    print(data)
    return web.Response(text='ok')


async def run_server():
    # config ssl
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('cert.pem', 'key.pem')

    # config web server
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()

    # start web server
    site = web.TCPSite(runner, socket.gethostbyname(
        socket.gethostname()), 443, ssl_context=ssl_context)
    await site.start()
    # print how to connect to webhook
    print(
        f'Webhook is running on https://{socket.gethostbyname(socket.gethostname())}:443/webhook')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(run_server())
    loop.run_forever()
