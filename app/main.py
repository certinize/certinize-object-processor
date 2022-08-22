import fastapi

from app import config, events
from app.api import routers


def get_application() -> fastapi.FastAPI:
    app_ = fastapi.FastAPI(debug=config.settings.debug, version=config.settings.version)

    app_.add_event_handler(  # type: ignore
        "startup", events.create_start_app_handler(app_)
    )
    app_.add_event_handler(  # type: ignore
        "shutdown", events.create_stop_app_handler(app_)
    )

    app_.include_router(routers.router)
    return app_


app = get_application()
