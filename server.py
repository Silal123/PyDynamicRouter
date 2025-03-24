import os
import importlib.util
import inspect
import asyncio
from pathlib import Path
from aiohttp import web

class DynamicRouter:
    def __init__(self, base_dir, routes_dir="routes", static_dir="static"):
        self.base_dir = Path(base_dir)
        self.routes_dir = self.base_dir / routes_dir
        self.static_dir = self.base_dir / static_dir
        self.app = web.Application()

    def setup_static_files(self, url_prefix="/"):
        if self.static_dir.exists() and self.static_dir.is_dir():
            self.app.router.add_static(url_prefix, self.static_dir)
        else:
            return

    def discover_routes(self):
        for path in self.routes_dir.glob('**/*'):
            relative_path = path.relative_to(self.routes_dir)

            url_parts = []
            for part in relative_path.parts:
                if not part.startswith('+'):
                    url_parts.append(part)

            url = '/' + '/'.join(url_parts) if url_parts else '/'

            if path.is_file() and not url.endswith('/'):
                url = url.split('/', 1)[0] or '/'

            if path.is_file():
                if path.name == '+server.py':
                    self._register_server_handlers(path, url)
                elif path.name == '+page.html':
                    self._register_html_page(path, url)


    def _register_server_handlers(self, server_path, url):
        module_name = f"routes.{server_path.relative_to(self.routes_dir).with_suffix('').as_posix().replace('/', '.')}"
        spec = importlib.util.spec_from_file_location(module_name, server_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        http_methods = {
            'GET': web.get,
            'POST': web.post,
            'PUT': web.put,
            'DELETE': web.delete,
            'PATCH': web.patch,
            'HEAD': web.head,
            'OPTIONS': web.options
        }
        
        for name, func in inspect.getmembers(module, inspect.isfunction):
            for method_name, decorator in http_methods.items():
                if hasattr(func, '_http_method') and func._http_method == method_name:
                    self.app.router.add_route(method_name, url, func)
        
    def _register_html_page(self, page_path, url):
        async def serve_html(request):
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        
        self.app.router.add_get(url, serve_html)

    def run(self, host='0.0.0.0', port=8080):
        web.run_app(self.app, host=host, port=port)


def GET(func):
    func._http_method = 'GET'
    return func

def POST(func):
    func._http_method = 'POST'
    return func

def PUT(func):
    func._http_method = 'PUT'
    return func

def DELETE(func):
    func._http_method = 'DELETE'
    return func

def PATCH(func):
    func._http_method = 'PATCH'
    return func

def HEAD(func):
    func._http_method = 'HEAD'
    return func

def OPTIONS(func):
    func._http_method = 'OPTIONS'
    return func

if __name__ == "__main__":
    router = DynamicRouter(os.path.dirname(os.path.abspath(__file__)))
    router.discover_routes()
    router.setup_static_files()
    router.run()