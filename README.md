# Dynamic router for Python
This is a dynamic router for aiohttp in python.

## Usage
### Running the Server
```python
router = DynamicRouter(os.path.dirname(os.path.abspath(__file__)))
router.discover_routes()
router.setup_static_files()
router.run()
```