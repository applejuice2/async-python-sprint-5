from .auth import router as router_auth
from .file import router as router_file

routers = [
    router_auth,
    router_file,
]
