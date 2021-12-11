from app.container import Container
from app.views import setup_views


def create_app():
    container = Container()
    container.config.from_yaml('./config.yml')

    app = container.app()
    app.container = container

    setup_views(container)

    return app
