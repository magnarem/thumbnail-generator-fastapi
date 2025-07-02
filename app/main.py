from .api import router
from .core.config import settings
from .core.setup import create_application

# Initialize and create the app
def create_app():
    app = create_application(router=router, settings=settings)
    return app
