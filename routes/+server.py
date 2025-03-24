from server import GET
from aiohttp import web

@GET
async def get(request):
    return web.Response(text="Main")