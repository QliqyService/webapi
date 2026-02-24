from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger as LOGGER
from starlette.staticfiles import StaticFiles

from app.routers import *
from app.routers.api.public import router as public_router
from app.services import Services
from app.routers.streaming import account_linking_router
from app.settings import get_settings


class Application(FastAPI):
    """Setting up and preparing the launch of the service"""

    def __init__(self):
        self.settings = get_settings()
        self.services = Services()
        self.logger = self.settings.configure_logging()

        super().__init__(
            title=self.settings.APP_TITLE,
            description=self.settings.APP_DESCRIPTION,
            root_path_in_servers=True,
            docs_url="/api/docs",
            openapi_url = "/api/openapi.json",
            redoc_url = "/api/redoc",
            version=self.settings.APP_RELEASE,
        )
        self.run_startup_actions()

    def run_startup_actions(self) -> None:
        self.add_middlewares()
        self.include_routers()
        self.add_startup_event_handlers()

    def mount_static(self) -> None:
        self.mount("/static", StaticFiles(directory="app/static"), name="static")

    def include_routers(self) -> None:
        self.include_router(api_router)
        self.include_router(pages_router)
        self.include_router(account_linking_router)
        self.include_router(public_router, prefix="/public", tags=["Public"])
        LOGGER.debug("[MAIN] Routers added")

    def add_middlewares(self) -> None:
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        LOGGER.debug("[MAIN] Middlewares added")

    def add_startup_event_handlers(self) -> None:
        services = self.services.get_external_services()
        for service in services:
            self.add_event_handler("startup", service.start)
            LOGGER.debug(f"[MAIN] Started: {service}")


app = Application()