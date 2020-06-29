from sanic import Sanic
from databases import Database
from environs import Env
from project.lab_svr.labsettings import LabSettings
from project.lab_svr.routes import setup_routes

lab_svr_app = Sanic(__name__)


def setup_lab_database():
    lab_svr_app.db = Database(lab_svr_app.config.DB_URL)

    @lab_svr_app.listener('after_server_start')
    async def connect_to_db(*args, **kwargs):
        await lab_svr_app.db.connect()

    @lab_svr_app.listener('after_server_stop')
    async def disconnect_from_db(*args, **kwargs):
        await lab_svr_app.db.disconnect()


def init():
    env = Env()
    env.read_env()

    lab_svr_app.config.from_object(LabSettings)
    setup_lab_database()
    setup_routes(lab_svr_app)

    lab_svr_app.run(
        host=lab_svr_app.config.HOST,
        port=lab_svr_app.config.PORT,
        debug=lab_svr_app.config.DEBUG,
        auto_reload=lab_svr_app.config.DEBUG,
    )
