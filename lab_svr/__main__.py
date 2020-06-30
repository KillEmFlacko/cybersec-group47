from sanic import Sanic
from databases import Database
from environs import Env
from sanic.log import logger
from sanic import response

from lab_svr.settings import Settings
from lab_svr.views import ShareView

lab_svr_app = Sanic(__name__)


def setup_lab_database():
    lab_svr_app.db = Database(lab_svr_app.config.DB_URL)

    @lab_svr_app.listener('after_server_start')
    async def connect_to_db(*args, **kwargs):
        try:
            await lab_svr_app.db.connect()
        except:
            logger.error("DB Connection Error")

    @lab_svr_app.listener('after_server_stop')
    async def disconnect_from_db(*args, **kwargs):
        try:
            await lab_svr_app.db.disconnect()
        except:
            logger.error("DB Disconnection Error")

def setup_routes(app):
    @app.route("/")
    async def test(request):
        return response.text("OK")

    app.add_route(ShareView.as_view(), '/new_share')

def init():
    env = Env()
    env.read_env()

    lab_svr_app.config.from_object(Settings)
    setup_lab_database()
    setup_routes(lab_svr_app)

    lab_svr_app.run(
        host=lab_svr_app.config.HOST,
        port=lab_svr_app.config.PORT,
        debug=lab_svr_app.config.DEBUG,
        auto_reload=lab_svr_app.config.DEBUG,
    )


init()
