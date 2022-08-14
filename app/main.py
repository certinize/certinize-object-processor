import fastapi

import app.api.routers as routers
import app.config as config
from app import events


def get_application() -> fastapi.FastAPI:
    app = fastapi.FastAPI(debug=config.settings.debug, version=config.settings.version)

    app.add_event_handler(  # type: ignore
        "startup", events.create_start_app_handler(app)
    )
    app.add_event_handler(  # type: ignore
        "shutdown", events.create_stop_app_handler(app)
    )

    app.include_router(routers.router)
    return app


app = get_application()
