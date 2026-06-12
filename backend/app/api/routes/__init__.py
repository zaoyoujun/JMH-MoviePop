from .movies import router as movies_router
from .openlist import router as openlist_router
from .sources import router as sources_router
from .scan import router as scan_router

__all__ = ["movies_router", "openlist_router", "sources_router", "scan_router"]
