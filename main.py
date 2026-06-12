import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database.connection import init_db
from scheduler.jobs import start_scheduler
from routers.leads import router as leads_router
from routers.dashboard import router as dashboard_router

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Starting scheduler...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(title="ShopRocket Lead Pipeline", version="1.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(dashboard_router)
app.include_router(leads_router)
