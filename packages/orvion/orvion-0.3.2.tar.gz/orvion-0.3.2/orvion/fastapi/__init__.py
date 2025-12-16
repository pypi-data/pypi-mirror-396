"""FastAPI integration for Orvion SDK"""

from typing import TYPE_CHECKING

from orvion.fastapi.decorators import require_payment
from orvion.fastapi.middleware import OrvionMiddleware, _scan_and_register_routes
from orvion.fastapi.routers import (
    create_full_router,
    create_health_router,
    create_payment_router,
)

if TYPE_CHECKING:
    from fastapi import FastAPI
    from orvion.client import OrvionClient


async def sync_routes(app: "FastAPI", client: "OrvionClient") -> int:
    """
    Register all @require_payment decorated routes with Orvion.

    Usage:
        from orvion import OrvionClient
        from orvion.fastapi import sync_routes, OrvionMiddleware, create_payment_router

        # Create single client instance
        client = OrvionClient(api_key=API_KEY, base_url=BASE_URL)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await sync_routes(app, client)
            yield
            await client.close()

        app = FastAPI(lifespan=lifespan)
        app.add_middleware(OrvionMiddleware, client=client, register_on_first_request=False)
        app.include_router(create_payment_router(client))

    Args:
        app: The FastAPI application instance
        client: OrvionClient instance

    Returns:
        Count of routes registered
    """
    return await _scan_and_register_routes(app, client)


__all__ = [
    # Middleware & Decorators
    "OrvionMiddleware",
    "require_payment",
    "sync_routes",
    # Pre-built Routers
    "create_payment_router",
    "create_health_router",
    "create_full_router",
]
