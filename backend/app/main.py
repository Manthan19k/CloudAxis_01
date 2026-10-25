from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()
from app.core.exceptions import register_exception_handlers
from app.api import auth, health, dashboard, servers, vms, storage, network, alerts, monitoring, inventory, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Initialize database and seed if requested
    if os.getenv("SEED_ON_STARTUP", "false").lower() == "true":
        from app.core.database import Base, engine
        from app.dependencies import (
            get_user_repo, get_server_repo, get_vm_repo, get_storage_repo,
            get_network_repo, get_alert_repo, get_monitoring_repo, get_inventory_repo,
            async_session_maker
        )
        from app.services.seed_service import SeedService
        
        print("Initializing database...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("Seeding database...")
        async with async_session_maker() as session:
            seed_service = SeedService(
                user_repo=get_user_repo(session),
                server_repo=get_server_repo(session),
                vm_repo=get_vm_repo(session),
                storage_repo=get_storage_repo(session),
                network_repo=get_network_repo(session),
                alert_repo=get_alert_repo(session),
                monitoring_repo=get_monitoring_repo(session),
                inventory_repo=get_inventory_repo(session)
            )
            await seed_service.seed_all()
            await session.commit()
            
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register exception handlers
register_exception_handlers(app)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(servers.router, prefix=settings.API_V1_STR)
app.include_router(vms.router, prefix=settings.API_V1_STR)
app.include_router(storage.router, prefix=settings.API_V1_STR)
app.include_router(network.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(monitoring.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
