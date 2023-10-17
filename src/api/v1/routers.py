from .auth import router as router_auth
from .file import router as router_file
from .monitoring import router as router_monitoring

routers = [
    router_auth,
    router_file,
    router_monitoring,
]
