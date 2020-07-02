import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from numpy.random._generator import Generator
from randomgen.aes import AESCounter
from sanic import Sanic, response
from databases import Database
from environs import Env
from sanic.log import logger
from sanic_scheduler import SanicScheduler, task
from datetime import timedelta

from sqlalchemy import String
from sqlalchemy.orm import Session

from lab_svr.tables import infects, contacts
import json
from sqlalchemy.sql.expression import func, select, or_, bindparam
from sqlalchemy.sql import text
from datetime import datetime

from lab_svr.settings import Settings
from lab_svr.views import ShareView

lab_svr_app = Sanic(__name__)
scheduler = SanicScheduler(lab_svr_app)
hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
iso_format = '%Y-%m-%d'


@lab_svr_app.route('/daily_task')
# @task(start=timedelta(seconds=5), period=timedelta(seconds=10))
async def daily_task(req):
    app = req.app
    logger.info("DAILY TASK")
    query = select([func.coalesce(func.max(infects.c.id), -1)])
    record = await app.db.fetch_all(query)
    last_id = record[0][0]
    params = {'last_id': last_id}
    resp = requests.get('https://localhost:8080/', params=params, verify='ca_certs')
    rows_list = resp.json()['skts']

    output_str = 'DAY\tPART\tEPHID\n'
    insert_txt = '''INSERT INTO "infect"("skt","nonce","created_date","start_date")
    VALUES
    '''
    for rec in rows_list:
        insert_txt += "( '"+rec['skt']+"','"+rec['nonce']+"','"+rec['created_date']+"','"+rec['start_date']+"'),"
        start_date = datetime.strptime(rec['start_date'], iso_format)
        created_date = datetime.strptime(rec['created_date'], iso_format)
        days = (created_date - start_date).days
        act_skt = bytes.fromhex(rec['skt'])
        try:
            act_nonce = bytes.fromhex(rec['nonce'])
        except (TypeError, KeyError):
            act_nonce = None

        hash_out_str = None
        if act_nonce is not None:
            h = hash.copy()
            h.update(act_skt + act_nonce)
            hash_out = h.finalize()
            hash_out_str = hash_out.hex()

        for i in range(0, days):
            prf = hmac.HMAC(act_skt, hashes.SHA256(), backend=default_backend())
            prf.update(b"broadcast key")
            prf_out = prf.finalize()
            bit_gen = AESCounter(key=int.from_bytes(prf_out[16:], "big"))
            gen = Generator(bit_gen)
            for j in range(0, app.config.DAY_PARTS):
                ephid = gen.bytes(16)
                query_txt = text('SELECT "DELETE_FAKE"(:ephid,:hash)')
                query_txt = query_txt.bindparams(ephid=ephid.hex(), hash=hash_out_str)
                result = await app.db.execute(query_txt)
                if result > 0:
                    output_str += str(i) + '\t' + str(j) + '\t' + ephid.hex() + '\n'
                if app.config.DEBUG:
                    logger.info('EphID : ' + ephid.hex() + ', SKt : ' + act_skt.hex())
                    logger.info("Fake contacts found : " + str(result) + ', Nonce : ' + str(act_nonce or 'None'))
            h = hash.copy()
            h.update(act_skt)
            act_skt = h.finalize()
    # TODO Insert

    return response.text(insert_txt + '\n' + 'OK')


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

    ssl = {'cert': lab_svr_app.config.CERT, 'key': lab_svr_app.config.KEY}
    lab_svr_app.run(
        host=lab_svr_app.config.HOST,
        port=lab_svr_app.config.PORT,
        debug=lab_svr_app.config.DEBUG,
        auto_reload=lab_svr_app.config.DEBUG,
        ssl=ssl,
    )


init()
