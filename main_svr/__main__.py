from databases import Database
from environs import Env
from sanic import Sanic
from sanic.log import logger

from main_svr.settings import Settings
from main_svr.views import MainView

main_svr_app = Sanic(__name__)


def setup_lab_database():
    main_svr_app.db = Database(main_svr_app.config.DB_URL)

    @main_svr_app.listener('after_server_start')
    async def connect_to_db(*args, **kwargs):
        try:
            await main_svr_app.db.connect()
            logger.info("DB connected")
        except:
            logger.error("DB Connection Error")

    @main_svr_app.listener('after_server_stop')
    async def disconnect_from_db(*args, **kwargs):
        try:
            await main_svr_app.db.disconnect()
            logger.info("DB disconnected")
        except:
            logger.error("DB Disconnection Error")


def init():
    env = Env()
    env.read_env()

    main_svr_app.config.from_object(Settings)
    setup_lab_database()
    main_svr_app.add_route(MainView.as_view(), '/')

    ssl = {'cert': main_svr_app.config.CERT, 'key': main_svr_app.config.KEY}
    main_svr_app.run(
        host=main_svr_app.config.HOST,
        port=main_svr_app.config.PORT,
        debug=main_svr_app.config.DEBUG,
        auto_reload=main_svr_app.config.DEBUG,
        ssl=ssl,
    )


init()
