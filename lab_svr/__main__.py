from databases import Database
from environs import Env
from sanic import Sanic
from sanic.log import logger
from sanic_scheduler import SanicScheduler

from lab_svr.settings import Settings
from lab_svr.tasks import setup_tasks
from lab_svr.views import ShareView

lab_svr_app = Sanic(__name__)
scheduler = SanicScheduler(lab_svr_app)


def setup_lab_database():
    lab_svr_app.db = Database(lab_svr_app.config.DB_URL)

    @lab_svr_app.listener('after_server_start')
    async def connect_to_db(*args, **kwargs):
        try:
            await lab_svr_app.db.connect()
            logger.info("DB connected")
        except:
            logger.error("DB Connection Error")

    @lab_svr_app.listener('after_server_stop')
    async def disconnect_from_db(*args, **kwargs):
        try:
            await lab_svr_app.db.disconnect()
            logger.info("DB disconnected")
        except:
            logger.error("DB Disconnection Error")


def init():
    env = Env()
    env.read_env()

    lab_svr_app.config.from_object(Settings)
    setup_lab_database()
    lab_svr_app.add_route(ShareView.as_view(), '/')
    setup_tasks()

    ssl = {'cert': lab_svr_app.config.CERT, 'key': lab_svr_app.config.KEY}
    lab_svr_app.run(
        host=lab_svr_app.config.HOST,
        port=lab_svr_app.config.PORT,
        debug=lab_svr_app.config.DEBUG,
        auto_reload=lab_svr_app.config.DEBUG,
        ssl=ssl,
    )


init()
